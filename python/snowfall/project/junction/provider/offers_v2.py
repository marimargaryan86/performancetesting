import dataclasses
import datetime
from typing import AsyncIterator, Callable, Generic, Sequence, TypeVar

import tenacity
from aiostream import stream
from google.protobuf import message

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.provider import repository
from snowfall.project.junction.provider.segment_matcher import SegmentMatcher
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import models_pb2

_SearchCriteriaTask = TypeVar("_SearchCriteriaTask", bound=message.Message)
_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
TripOfferSearchCriteriaTaskGenerator = Callable[
    [offers_pb2.TripOfferSearch],
    list[_SearchCriteriaTask],
]
TripOfferSearchCriteriaGenerator = Callable[[_SearchCriteriaTask], _SearchCriteria]
OfferGroupGenerator = Callable[[_SearchCriteria], AsyncIterator[offers_pb2.OfferGroup]]
_DEFAULT_ALLOWED_WINDOW_TD = datetime.timedelta(minutes=0)


@dataclasses.dataclass(frozen=True)
class OfferSearchImplementation(Generic[_SearchCriteriaTask, _SearchCriteria]):
    search_criteria_task_generator: TripOfferSearchCriteriaTaskGenerator[
        _SearchCriteriaTask
    ]
    search_criteria_generator: TripOfferSearchCriteriaGenerator[
        _SearchCriteriaTask,
        _SearchCriteria,
    ]
    offer_group_cache_key_generator: repository.CacheKeyGenerator[_SearchCriteria]
    offer_group_generator: repository.OfferGroupGenerator[_SearchCriteria]
    allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD


class TripOfferSearcher(Generic[_SearchCriteriaTask, _SearchCriteria]):
    def __init__(
        self,
        task_generator: TripOfferSearchCriteriaTaskGenerator[_SearchCriteriaTask],
        criteria_generator: TripOfferSearchCriteriaGenerator[  # noqa: WPS320
            _SearchCriteriaTask,
            _SearchCriteria,
        ],
        offer_group_repository: repository.OfferGroupRepository[_SearchCriteria],
        allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD,
    ):
        self._allowed_window_td = allowed_window_td
        self._offer_group_repository = offer_group_repository
        self._search_criteria_task_generator = task_generator
        self._search_criteria_generator = criteria_generator

    async def search(
        self,
        search: offers_pb2.TripOfferSearch,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        search_criterion_tasks = self._search_criteria_task_generator(search)
        generators = stream.merge(
            *(
                self._process_search_criterion_task(search_criterion_task)
                for search_criterion_task in search_criterion_tasks
            ),
        )

        async with generators.stream() as offer_groups:
            async for offer_group in offer_groups:
                yield offer_group

    async def _process_search_criterion_task(
        self,
        task: _SearchCriteriaTask,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        # TODO: shared protobuf, or type intersection support in Python
        if not hasattr(task, "segments"):  # noqa: WPS421
            raise TypeError

        search_criteria = self._search_criteria_generator(task)
        segment_matcher = SegmentMatcher(
            segments=task.segments,
            allowed_window_td=self._allowed_window_td,
        )

        for attempt in tenacity.Retrying(stop=tenacity.stop_after_attempt(3)):
            with attempt:
                offer_groups = self._offer_group_repository.find(search_criteria)

        async for offer_group in offer_groups:
            if segment_matcher.offer_group_matches(offer_group):
                set_segment_ids(task.segments, offer_group)

                yield offer_group


class TripOfferSearchConsumer(Generic[_SearchCriteriaTask, _SearchCriteria]):
    def __init__(
        self,
        consumer: amqp_consumer.Consumer[offers_amqp_pb2.TripOfferSearchTask],
        producer: amqp_producer.Producer,
        trip_offer_searcher: TripOfferSearcher[_SearchCriteriaTask, _SearchCriteria],
        pay_company_id: str,
    ):
        self._consumer = consumer
        self._producer = producer
        self._trip_offer_searcher = trip_offer_searcher
        self._pay_company_id = pay_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripOfferSearchTask],
    ) -> None:
        offer_groups = self._trip_offer_searcher.search(
            amqp_message.body.search,
        )

        async for offer_group in offer_groups:
            await self._producer.publish(
                msg=offers_amqp_pb2.TripOfferSearchResult(
                    offer_search_id=amqp_message.body.offer_search_id,
                    offer=offer_group,
                    provider_company_id=self._pay_company_id,
                ),
                routing_key="offers.result.trip",
            )


def create_trip_offer_search_consumer(
    amqp_connection: amqp_types.Connection,
    redis_client: redis.Client[bytes],
    implementation: OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria],
    app_name: str,
    pay_company_id: str,
) -> TripOfferSearchConsumer[_SearchCriteriaTask, _SearchCriteria]:
    producer = amqp_producer.Producer(
        connection=amqp_connection,
        exchange=amqp_types.Exchange("offers"),
    )

    return TripOfferSearchConsumer(
        consumer=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_offers".format(app_name),
            binds=[
                (amqp_types.Exchange("offers"), "offers.search.trip"),
            ],
            middleware_stack=[
                trackable.ReportingMiddleware(
                    status_reporter=trackable.StatusReporter(
                        producer=producer,
                    ),
                ).execute,
            ],
        ),
        producer=producer,
        trip_offer_searcher=TripOfferSearcher(
            task_generator=implementation.search_criteria_task_generator,
            criteria_generator=implementation.search_criteria_generator,
            allowed_window_td=implementation.allowed_window_td,
            offer_group_repository=repository.OfferGroupRepository(
                offer_group_cache_key_func=implementation.offer_group_cache_key_generator,
                redis=redis_client,
                offer_group_generator=implementation.offer_group_generator,
            ),
        ),
        pay_company_id=pay_company_id,
    )


def set_segment_ids(
    search_segments: Sequence[models_pb2.Segment],
    offer: offers_pb2.OfferGroup,
) -> None:
    for segment_index, segment in enumerate(offer.segments):
        segment.segment_id = search_segments[segment_index].id
