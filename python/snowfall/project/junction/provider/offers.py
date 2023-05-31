from __future__ import annotations

import dataclasses
import datetime
from typing import AsyncIterator, Callable, Generic, Mapping, Sequence, TypeVar

from aiostream import stream
from google.protobuf import message
from grpc import aio

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as legacy_offers_pb2,
)
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.project.junction.provider import repository
from snowfall.project.junction.provider.segment_matcher import SegmentMatcher
from snowfall.project.junction.provider.v1alpha import offers_pb2, offers_pb2_grpc
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.transport.grpc import service

_SearchCriteriaTask = TypeVar("_SearchCriteriaTask", bound=message.Message)
_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
TripOfferSearchCriteriaTaskGenerator = Callable[
    [legacy_offers_pb2.TripOfferSearch],
    list[_SearchCriteriaTask],
]
TripOfferSearchCriteriaGenerator = Callable[[_SearchCriteriaTask], _SearchCriteria]
OfferGroupGenerator = Callable[
    [_SearchCriteria],
    AsyncIterator[legacy_offers_pb2.OfferGroup],
]
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

    @classmethod
    def from_implementation(
        cls,
        implementation: OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria],
        redis_client: redis.Client[bytes],
    ) -> TripOfferSearcher[_SearchCriteriaTask, _SearchCriteria]:
        return cls(
            task_generator=implementation.search_criteria_task_generator,
            criteria_generator=implementation.search_criteria_generator,
            allowed_window_td=implementation.allowed_window_td,
            offer_group_repository=repository.OfferGroupRepository(
                offer_group_cache_key_func=implementation.offer_group_cache_key_generator,
                redis=redis_client,
                offer_group_generator=implementation.offer_group_generator,
            ),
        )

    async def search(
        self,
        search: legacy_offers_pb2.TripOfferSearch,
    ) -> AsyncIterator[legacy_offers_pb2.OfferGroup]:
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
    ) -> AsyncIterator[legacy_offers_pb2.OfferGroup]:
        # TODO: shared protobuf, or type intersection support in Python
        if not hasattr(task, "segments"):  # noqa: WPS421
            raise TypeError

        search_criteria = self._search_criteria_generator(task)
        segment_matcher = SegmentMatcher(
            segments=task.segments,
            allowed_window_td=self._allowed_window_td,
        )

        offer_groups = self._offer_group_repository.find(search_criteria)

        async for offer_group in offer_groups:
            if segment_matcher.offer_group_matches(offer_group):
                set_segment_ids(task.segments, offer_group)

                yield offer_group


class OfferSearchService(service.Service, offers_pb2_grpc.OfferServiceServicer):
    def __init__(
        self,
        trip_offer_searcher: TripOfferSearcher[_SearchCriteriaTask, _SearchCriteria],
    ):
        self._trip_offer_searcher = trip_offer_searcher

    def get_name(self) -> str:
        return offers_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: aio.Server) -> None:
        offers_pb2_grpc.add_OfferServiceServicer_to_server(self, server)

    async def SearchOffers(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.SearchOffersRequest,
        context: aio.ServicerContext,
    ) -> offers_pb2.SearchOffersResponse:
        if request.WhichOneof("offer_search_task") != "trip_offer_search_task":
            return offers_pb2.SearchOffersResponse()

        return offers_pb2.SearchOffersResponse(
            trip_offer_search_results=offers_pb2.TripOfferSearchResults(
                results=[
                    offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=request.trip_offer_search_task.offer_search_id,
                        offer=offer_group,
                        provider_company_id="",  # TODO: real value
                        provider_name="",  # TODO: real value
                    )
                    async for offer_group in self._trip_offer_searcher.search(
                        request.trip_offer_search_task.search,
                    )
                ],
            ),
        )


class TripOfferSearchConsumer(Generic[_SearchCriteriaTask, _SearchCriteria]):
    def __init__(  # noqa: WPS211
        self,
        consumer: amqp_consumer.Consumer[offers_amqp_pb2.TripOfferSearchTask],
        producer: amqp_producer.Producer,
        trip_offer_searcher: TripOfferSearcher[_SearchCriteriaTask, _SearchCriteria],
        pay_company_id: str,
        provider_name: str,
        reseller_providers: Mapping[str, Sequence[str]],
    ):
        self._consumer = consumer
        self._producer = producer
        self._trip_offer_searcher = trip_offer_searcher
        self._pay_company_id = pay_company_id
        self._provider_name = provider_name
        self._reseller_providers = reseller_providers

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripOfferSearchTask],
    ) -> None:
        if self._provider_blocked_for_reseller(amqp_message.body.reseller_id):
            return

        try:
            await self._publish_trip_offer_search_results(amqp_message)
        except repository.OfferCacheLockError:
            await amqp_message.nack(requeue=True)

    def _provider_blocked_for_reseller(self, reseller_id: str) -> bool:
        return self._provider_name not in self._reseller_providers.get(reseller_id, [])

    async def _publish_trip_offer_search_results(
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
                    provider_name=self._provider_name,
                ),
                routing_key="offers.result.trip",
            )


def create_trip_offer_search_consumer(  # noqa:WPS211
    amqp_connection: amqp_types.Connection,
    redis_client: redis.Client[bytes],
    implementation: OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria],
    app_name: str,
    pay_company_id: str,
    provider_name: str,
    reseller_providers: Mapping[str, Sequence[str]],
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
        trip_offer_searcher=TripOfferSearcher.from_implementation(
            implementation=implementation,
            redis_client=redis_client,
        ),
        pay_company_id=pay_company_id,
        provider_name=provider_name,
        reseller_providers=reseller_providers,
    )


def set_segment_ids(
    search_segments: Sequence[models_pb2.Segment],
    offer: legacy_offers_pb2.OfferGroup,
) -> None:
    for segment_index, segment in enumerate(offer.segments):
        segment.segment_id = search_segments[segment_index].id
