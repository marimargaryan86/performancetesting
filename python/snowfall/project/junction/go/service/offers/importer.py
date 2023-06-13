import asyncio
import contextlib
import datetime
from typing import Sequence, Union

import prometheus_client
import structlog
from pymongo import errors

from snowfall.project.junction.go.service.gateway.v1alpha import (
    offers_pb2,
    offers_pb2_grpc,
)
from snowfall.project.junction.go.service.offers import (
    aggregator,
    offers,
    pay_quotes,
    price_quotes,
)
from snowfall.project.junction.go.service.offers.v1alpha import amqp_pb2
from snowfall.project.junction.go.service.offers.v1alpha.models_pb2 import (
    OfferGroup,
    OfferSearch,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer, trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1 import amqp_pb2 as trackable_pb2

ExpectedMessages = Union[
    amqp_pb2.TripOfferSearchResult,
    trackable_pb2.Trackable,
    amqp_pb2.TripOfferSearchTask,
]
_PROVIDERS_TO_DISABLED_OPERATORS = dict[str, list[str]]
RESELLERS_TO_PROVIDER_OPERATORS = dict[str, _PROVIDERS_TO_DISABLED_OPERATORS]

_histogram_search_time = prometheus_client.Histogram(
    "offers_search_time_seconds",
    "Time needed to complete offer searches (in seconds).",
    buckets=prometheus.BUCKETS,
)


class SkippedOfferError(Exception):
    """Raised when an offer is skipped."""


class SkippedPriceQuoteError(Exception):
    """Raised when price quote is skipped."""


class StatusHandler(trackable.AnySizeStatusHandler):
    def __init__(
        self,
        redis: types.Client[str],
        repository: offers.OfferSearchRepository,
    ) -> None:
        super().__init__(redis=redis)

        self._repository = repository

    async def on_message(self, msg: trackable_pb2.Trackable) -> None:
        if msg.event == msg.Event.EVENT_NACKED:
            msg.event = msg.Event.EVENT_ACKED
        await super().on_message(msg)

    async def _get_status_and_expiry_by_id(
        self,
        trackable_id: str,
    ) -> tuple[trackable_pb2.Trackable.Status.ValueType, datetime.datetime]:
        record = await self._repository.find_by_id(trackable_id)

        return (
            record.status if record else trackable_pb2.Trackable.STATUS_UNSPECIFIED,
            (
                protobuf.protobuf_to_datetime(record.expires_at)
                if record
                else datetime.datetime.now(tz=datetime.timezone.utc)
            ),
        )

    async def _on_completed(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await asyncio.sleep(2)  # TODO: solve race condition properly
        search = await self._repository.mark_as_completed(msg.id)
        created_at = protobuf.protobuf_to_datetime(search.created_at)
        updated_at = protobuf.protobuf_to_datetime(search.updated_at)

        _histogram_search_time.observe((updated_at - created_at).total_seconds())

    async def _on_failed(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await self._repository.mark_as_failed(msg.id)

    async def _on_processing(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await self._repository.mark_as_processing(msg.id)


class OfferImporter(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[ExpectedMessages],
        trip_offers: offers.TripOfferRepository,
        offer_aggregator: aggregator.OfferAggregator,
        redis: types.Client[str],
        status_handler: StatusHandler,
        offer_searches: offers.OfferSearchRepository,
        pay_quote_fetcher: pay_quotes.PayQuoteFetcher,
        reseller_disabled_operators: RESELLERS_TO_PROVIDER_OPERATORS,
        gateway_stubs: offers_pb2_grpc.OfferServiceStub,
        gateway_timeout: datetime.timedelta,
    ):
        self._consumer = consumer_obj
        self._offers = trip_offers
        self._aggregator = offer_aggregator
        self._logger = structlog.get_logger(__name__)
        self._redis = redis
        self._status_handler = status_handler
        self._searches = offer_searches
        self._pay_quote_fetcher = pay_quote_fetcher
        self._reseller_disabled_operators = reseller_disabled_operators
        self._gateway_stubs = gateway_stubs
        self._gateway_timeout = gateway_timeout

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[ExpectedMessages],
    ) -> None:
        match message.body:
            case amqp_pb2.TripOfferSearchResult():
                offer_search = await self._searches.find_by_id(
                    message.body.offer_search_id,
                )

                if not offer_search:
                    raise SkippedOfferError()

                await self._process_trip_offer_search_result(offer_search, message.body)
            case trackable_pb2.Trackable():
                await self._status_handler.on_message(message.body)
            case amqp_pb2.TripOfferSearchTask():
                try:
                    await self._process_trip_offer_search(message.body)
                except Exception as err:
                    await self._searches.mark_as_failed(message.body.offer_search_id)
                    raise err

    async def _process_trip_offer_search(  # noqa: WPS217
        self,
        message: amqp_pb2.TripOfferSearchTask,
    ) -> None:
        offer_search = await self._searches.find_by_id(message.offer_search_id)

        if not offer_search:
            raise SkippedOfferError()

        await self._searches.mark_as_processing(offer_search.id)

        response = await self._gateway_stubs.EnqueueOfferSearch(
            offers_pb2.EnqueueOfferSearchRequest(
                trip_offer_search_task=message,
            ),
            timeout=self._gateway_timeout.total_seconds(),
        )

        # should be identical to what we've already
        # got, but let's not make any assumptions.
        gw_offer_search_id = response.id
        cutoff = datetime.datetime.now(tz=datetime.UTC) + self._gateway_timeout

        while datetime.datetime.now(tz=datetime.UTC) < cutoff:
            response = await self._gateway_stubs.PopOfferSearchResults(
                offers_pb2.PopOfferSearchResultsRequest(
                    id=gw_offer_search_id,
                ),
                timeout=self._gateway_timeout.total_seconds(),
            )

            await asyncio.gather(
                *[
                    self._process_trip_offer_search_result(offer_search, offer_result)
                    for offer_result in response.trip_offer_search_results.results
                ],
            )

            if not response.is_in_progress:
                break

            await asyncio.sleep(1)

        await self._searches.mark_as_completed(offer_search.id)

    async def _process_trip_offer_search_result(
        self,
        offer_search: OfferSearch,
        message: amqp_pb2.TripOfferSearchResult,
    ) -> None:
        disabled_operators = self._reseller_disabled_operators.get(
            offer_search.reseller_id,
            {},
        ).get(message.provider_name, [])

        if self._contains_disabled_operator(disabled_operators, message.offer):
            return

        redis_lock = "results:{0}".format(message.offer_search_id)
        message = await self._pay_quote_fetcher.handle_offer_search_result(
            message=message,
            session_token=offer_search.session_token,
            offer_search=offer_search,
        )

        async with self._redis.lock(redis_lock, timeout=10):
            try:
                await self._aggregator.aggregate(message)
            except aggregator.SkippedOfferError:
                self._logger.exception(
                    "An offer arrived too late",
                    offer_search_id=message.offer_search_id,
                )
                return

            with contextlib.suppress(errors.DuplicateKeyError):
                await self._offers.insert(message.offer)

    def _contains_disabled_operator(
        self,
        disabled_operators: Sequence[str],
        offer: OfferGroup,
    ) -> bool:
        return any(
            segment.vendor in disabled_operators
            or segment.operator in disabled_operators
            for segment in offer.segments
        )


class PriceQuoteImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripPriceQuoteResult],
        price_quotes_repository: price_quotes.PriceQuoteRepository,
        price_quotes_container_repository: price_quotes.PriceQuoteContainerRepository,
        pay_quote_fetcher: pay_quotes.PayQuoteFetcher,
    ):
        self._consumer = consumer_obj
        self._quotes = price_quotes_repository
        self._price_quotes_container_repository = price_quotes_container_repository
        self._pay_quote_fetcher = pay_quote_fetcher

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[amqp_pb2.TripPriceQuoteResult],
    ) -> None:
        price_quote_container = (
            await self._price_quotes_container_repository.find_by_id(
                message.body.price_quote_container_id,
            )
        )

        if not price_quote_container:
            raise SkippedPriceQuoteError()

        price_quote_message = await self._pay_quote_fetcher.handle_price_quote_result(
            message=message.body,
            price_quote_container=price_quote_container,
        )

        await self._quotes.add_to_container(
            price_quote_container_id=price_quote_message.price_quote_container_id,
            price_quote=price_quote_message.price_quote,
        )
