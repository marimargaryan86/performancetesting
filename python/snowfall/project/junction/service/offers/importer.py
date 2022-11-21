import contextlib
import datetime
from typing import Union

import structlog
from pymongo import errors

from snowfall.project.junction.service.offers import aggregator, offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer, trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import amqp_pb2 as trackable_pb2

ExpectedMessages = Union[
    amqp_pb2.TripOfferSearchResult,
    trackable_pb2.Trackable,
]


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
            protobuf.protobuf_to_datetime(record.expires_at)
            if record
            else datetime.datetime.now(tz=datetime.timezone.utc),
        )

    async def _on_completed(
        self,
        msg: trackable_pb2.Trackable,
    ) -> None:
        await self._repository.mark_as_completed(msg.id)

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
    ):
        self._consumer = consumer_obj
        self._offers = trip_offers
        self._aggregator = offer_aggregator
        self._logger = structlog.get_logger(__name__)
        self._redis = redis
        self._status_handler = status_handler

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
