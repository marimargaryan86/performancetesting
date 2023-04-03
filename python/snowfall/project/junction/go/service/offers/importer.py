import asyncio
import contextlib
import datetime
from typing import Union

import prometheus_client
import structlog
from pymongo import errors

from snowfall.project.junction.go.service.offers import (
    aggregator,
    offers,
    pay_quotes,
    price_quotes,
)
from snowfall.project.junction.go.service.offers.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer, trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import amqp_pb2 as trackable_pb2

ExpectedMessages = Union[
    amqp_pb2.TripOfferSearchResult,
    trackable_pb2.Trackable,
]

_histogram_search_time = prometheus_client.Histogram(
    "offers_search_time_seconds",
    "Time needed to complete offer searches (in seconds).",
    buckets=prometheus.BUCKETS,
)


class SkippedOfferError(Exception):
    """Raised when an offer is skipped."""


class StatusHandler(trackable.AnySizeStatusHandler):
    def __init__(
        self,
        redis: types.Client[str],
        repository: offers.OfferSearchRepository,
    ) -> None:
        super().__init__(redis=redis)

        self._repository = repository

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
    ):
        self._consumer = consumer_obj
        self._offers = trip_offers
        self._aggregator = offer_aggregator
        self._logger = structlog.get_logger(__name__)
        self._redis = redis
        self._status_handler = status_handler
        self._searches = offer_searches
        self._pay_quote_fetcher = pay_quote_fetcher

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[ExpectedMessages],
    ) -> None:
        match message.body:
            case amqp_pb2.TripOfferSearchResult():
                await self._process_trip_offer_search_result(message.body)
            case trackable_pb2.Trackable():
                await self._status_handler.on_message(message.body)

    async def _process_trip_offer_search_result(
        self,
        message: amqp_pb2.TripOfferSearchResult,
    ) -> None:
        redis_lock = "results:{0}".format(message.offer_search_id)

        offer_search = await self._searches.find_by_id(message.offer_search_id)

        if not offer_search:
            raise SkippedOfferError()

        message = await self._pay_quote_fetcher.convert_amounts_and_replace_ids(
            message=message,
            session_token=offer_search.session_token,
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


class PriceQuoteImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripPriceQuoteResult],
        price_quotes_repository: price_quotes.PriceQuoteRepository,
    ):
        self._consumer = consumer_obj
        self._quotes = price_quotes_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[amqp_pb2.TripPriceQuoteResult],
    ) -> None:
        await self._quotes.add_to_container(
            price_quote_container_id=message.body.price_quote_container_id,
            price_quote=message.body.price_quote,
        )
