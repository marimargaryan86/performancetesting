import asyncio
import contextlib
import datetime

import prometheus_client
from pymongo import errors as pymongo_errors

from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    searches_pb2,
    searches_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches import pay_quotes, repository
from snowfall.project.junction.rocket.service.searches.v1alpha import amqp_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer, trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1 import amqp_pb2 as trackable_pb2

ExpectedMessages = (
    amqp_pb2.SearchTaskResult | trackable_pb2.Trackable | amqp_pb2.SearchTask
)

_PROVIDERS_TO_DISABLED_OPERATORS = dict[str, list[str]]
RESELLERS_TO_PROVIDER_OPERATORS = dict[str, _PROVIDERS_TO_DISABLED_OPERATORS]

_histogram_search_time = prometheus_client.Histogram(
    "search_time_seconds",
    "Time needed to complete offer searches (in seconds).",
    buckets=prometheus.BUCKETS,
)


class SkippedSearchResultError(Exception):
    """Raised when an offer is skipped."""


class SkippedPriceQuoteError(Exception):
    """Raised when price quote is skipped."""


class StatusHandler(trackable.AnySizeStatusHandler):
    def __init__(
        self,
        redis: types.Client[str],
        search_repository: repository.SearchRepository,
    ) -> None:
        super().__init__(redis=redis)

        self._search_repository = search_repository

    async def on_message(self, msg: trackable_pb2.Trackable) -> None:
        if msg.event == msg.Event.EVENT_NACKED:
            msg.event = msg.Event.EVENT_ACKED
        await super().on_message(msg)

    async def _get_status_and_expiry_by_id(
        self,
        trackable_id: str,
    ) -> tuple[trackable_pb2.Trackable.Status.ValueType, datetime.datetime]:
        record = await self._search_repository.find_by_id(trackable_id)

        return (
            record.status if record else trackable_pb2.Trackable.STATUS_UNSPECIFIED,
            (
                protobuf.protobuf_to_datetime(record.expires_at)
                if record
                else datetime.datetime.now(tz=datetime.UTC)
            ),
        )

    async def _on_completed(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await asyncio.sleep(2)  # TODO(jyggen): solve race condition properly
        search = await self._search_repository.mark_as_completed(msg.id)
        created_at = protobuf.protobuf_to_datetime(search.created_at)
        updated_at = protobuf.protobuf_to_datetime(search.updated_at)

        _histogram_search_time.observe((updated_at - created_at).total_seconds())

    async def _on_failed(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await self._search_repository.mark_as_failed(msg.id)

    async def _on_processing(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await self._search_repository.mark_as_processing(msg.id)


class SearchResultImporter:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[ExpectedMessages],
        search_results: repository.SearchResultRepository,
        redis: types.Client[str],
        status_handler: StatusHandler,
        searches: repository.SearchRepository,
        gateway_stubs: searches_pb2_grpc.SearchServiceStub,
        gateway_timeout: datetime.timedelta,
        gateway_poll_sleep: int,
    ):
        self._consumer = consumer_obj
        self._search_results = search_results
        self._logger = stdout.get_logger()
        self._redis = redis
        self._status_handler = status_handler
        self._searches = searches
        self._gateway_stubs = gateway_stubs
        self._gateway_timeout = gateway_timeout
        self._gateway_poll_sleep = gateway_poll_sleep

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS217
        self,
        message: amqp_types.Message[ExpectedMessages],
    ) -> None:
        match message.body:
            case amqp_pb2.SearchTaskResult():
                search = await self._searches.find_by_id(
                    message.body.search_id,
                )

                if not search:
                    return

                await self._search_results.insert(message.body.search_result)
            case trackable_pb2.Trackable():
                await self._status_handler.on_message(message.body)
            case amqp_pb2.SearchTask():
                try:
                    await self._process_search(message.body)
                except Exception:
                    await self._searches.mark_as_failed(message.body.search_id)
                    raise

    async def _process_search(  # noqa: WPS217
        self,
        message: amqp_pb2.SearchTask,
    ) -> None:
        search = await self._searches.find_by_id(message.search_id)

        if not search:
            return

        await self._searches.mark_as_processing(search.id)

        response = await self._gateway_stubs.EnqueueSearch(
            searches_pb2.EnqueueSearchRequest(
                search_task=message,
            ),
            timeout=self._gateway_timeout.total_seconds(),
        )

        gw_search_id = response.id
        cutoff = datetime.datetime.now(tz=datetime.UTC) + self._gateway_timeout
        self._logger.info(
            "Starting to poll",
            now=datetime.datetime.now(tz=datetime.UTC).isoformat(),
        )

        while datetime.datetime.now(tz=datetime.UTC) < cutoff:
            await asyncio.sleep(self._gateway_poll_sleep)
            response = await self._gateway_stubs.PopSearchResults(
                searches_pb2.PopSearchResultsRequest(
                    id=gw_search_id,
                ),
                timeout=self._gateway_timeout.total_seconds(),
            )

            if response.search_task_results:
                with contextlib.suppress(pymongo_errors.BulkWriteError):
                    results = await self._search_results.insert_many(
                        [
                            search_task_result.search_result
                            for search_task_result in response.search_task_results
                        ],
                        ordered=False,
                    )

                    search_result_ids = [search_result.id for search_result in results]

                    await self._searches.add_search_result_ids(
                        search_id=search.id,
                        search_result_ids=search_result_ids,
                    )

            if not response.is_in_progress:
                break

            await asyncio.sleep(self._gateway_poll_sleep)

        self._logger.info(
            "Marking as completed",
            now=datetime.datetime.now(tz=datetime.UTC).isoformat(),
            cutoff=cutoff.isoformat(),
        )

        await self._searches.mark_as_completed(search.id)


class QuoteResultImporter:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.QuoteTaskResult],
        quotes: repository.QuoteRepository,
        pay_quotes_processor: pay_quotes.PayQuotes,
    ):
        self._consumer = consumer_obj
        self._quotes = quotes
        self._pay_quotes_processor = pay_quotes_processor

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS217
        self,
        message: amqp_types.Message[amqp_pb2.QuoteTaskResult],
    ) -> None:
        await self._quotes.upsert(message.body.quote)

        pay_quote = await self._pay_quotes_processor.create_pay_quote(
            amount=money.from_protobuf(message.body.quote.total_price).amount,
            reseller_currency=message.body.quote.reseller_currency,
            provider_currency=message.body.quote.total_price.currency_code,
            reseller_company_id=message.body.quote.reseller_pay_company_id,
            provider_pay_company_id=message.body.quote.pay_company_id,
            vertical_type=message.body.quote.vertical_type,
        )

        message.body.quote.pay_quote_id = pay_quote.quotation.id
        await self._quotes.upsert(message.body.quote)
