import datetime
from typing import AsyncIterator, Callable, Generic, Sequence, TypeVar

from google.protobuf import message

from snowfall.project.junction.provider import status
from snowfall.project.junction.provider.repository import (
    OfferCacheLockError,
    OfferGroupRepository,
)
from snowfall.project.junction.provider.segment_matcher import SegmentMatcher
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import amqp_pb2 as stdlib_amqp_pb2
from snowfall.stdlib.v1alpha import models_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
_CriteriaType = TypeVar("_CriteriaType")
TripOfferSearchMessages = (
    offers_amqp_pb2.TripOfferSearchTask | stdlib_amqp_pb2.Trackable
)
TripOfferSearchCriteriaGenerator = Callable[
    [offers_amqp_pb2.TripOfferSearchTask],
    list[_Proto],
]
OfferGroupGenerator = Callable[[_Proto], AsyncIterator[offers_pb2.OfferGroup]]
_DEFAULT_ALLOWED_WINDOW_TD = datetime.timedelta(minutes=0)


class TripOfferSearchConsumer(Generic[_Proto]):
    def __init__(
        self,
        consumer: amqp_consumer.Consumer[TripOfferSearchMessages],
        producer: trackable.TrackableProducer,
        generator: TripOfferSearchCriteriaGenerator[_Proto],
        status_handler: status.SubtaskStatusHandler,
    ):
        self._consumer = consumer
        self._producer = producer
        self._generator = generator
        self._status_handler = status_handler

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[TripOfferSearchMessages],
    ) -> None:
        match amqp_message.body:
            case offers_amqp_pb2.TripOfferSearchTask():
                await self._process_trip_offer_search_task(amqp_message.body)
            case stdlib_amqp_pb2.Trackable():
                await self._status_handler.on_message(amqp_message.body)

    async def _process_trip_offer_search_task(
        self,
        body: offers_amqp_pb2.TripOfferSearchTask,
    ) -> None:
        tasks = self._generator(body)

        await self._status_handler.set_expected_size(
            body.offer_search_id,
            len(tasks),
        )

        for task in tasks:
            await self._producer.publish(
                task,
                routing_key="offers.search.trip",
                trackable_id=body.offer_search_id,
            )


def create_trip_offer_search_consumer(
    amqp_connection: amqp_types.Connection,
    redis_client: redis_types.Client[str],
    criteria_generator: TripOfferSearchCriteriaGenerator[_Proto],
    internal_exchange_name: str,
) -> TripOfferSearchConsumer[_Proto]:
    return TripOfferSearchConsumer[_Proto](
        consumer=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_offers".format(internal_exchange_name),
            binds=[
                (amqp_types.Exchange("offers"), "offers.search.trip"),
                (
                    amqp_types.Exchange(internal_exchange_name),
                    trackable.to_tracking_key("offers.search.trip"),
                ),
            ],
        ),
        producer=trackable.TrackableProducer(
            amqp_producer.Producer(
                connection=amqp_connection,
                exchange=amqp_types.Exchange(internal_exchange_name),
            ),
        ),
        generator=criteria_generator,
        status_handler=status.SubtaskStatusHandler(
            reporter=trackable.StatusReporter(
                amqp_producer.Producer(
                    connection=amqp_connection,
                    exchange=amqp_types.Exchange("offers"),
                ),
            ),
            redis=redis_client,
            trackable_key=trackable.to_tracking_key("offers.search.trip"),
        ),
    )


def set_segment_ids(
    search_segments: Sequence[models_pb2.Segment],
    offer: offers_pb2.OfferGroup,
) -> None:
    for segment_index, segment in enumerate(offer.segments):
        segment.segment_id = search_segments[segment_index].id


class SearchCriteriaConsumer(Generic[_Proto, _CriteriaType]):
    def __init__(  # noqa: WPS211
        self,
        consumer: amqp_consumer.Consumer[_Proto],
        producer: amqp_producer.Producer,
        offer_group_repository: OfferGroupRepository[_CriteriaType],
        search_criteria_generator_func: Callable[[_Proto], _CriteriaType],
        allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD,
    ):
        self._consumer = consumer
        self._producer = producer
        self._offer_group_repository = offer_group_repository
        self._search_criteria_generator_func = search_criteria_generator_func
        self._allowed_window_td = allowed_window_td

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[_Proto],
    ) -> None:
        # todo: shared protobuf, or type intersection support in Python
        if not hasattr(  # noqa: WPS421, WPS337
            amqp_message.body,
            "segments",
        ) or not hasattr(  # noqa: WPS421
            amqp_message.body,
            "offer_search_id",
        ):
            raise TypeError

        segment_matcher = SegmentMatcher(
            segments=amqp_message.body.segments,
            allowed_window_td=self._allowed_window_td,
        )
        search_criteria = self._search_criteria_generator_func(amqp_message.body)
        try:
            offer_groups = self._offer_group_repository.find(search_criteria)
        except OfferCacheLockError:
            return await amqp_message.nack(requeue=True)

        async for offer_group in offer_groups:
            if segment_matcher.offer_group_matches(offer_group):
                set_segment_ids(amqp_message.body.segments, offer_group)
                await self._producer.publish(
                    msg=offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=amqp_message.body.offer_search_id,
                        offer=offer_group,
                    ),
                    routing_key="offers.result.trip",
                )
