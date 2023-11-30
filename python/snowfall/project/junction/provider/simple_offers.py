from __future__ import annotations

import asyncio
import dataclasses
import datetime
from collections.abc import AsyncIterator, Callable, Mapping, Sequence
from typing import Generic, TypeVar

from aio_pika import abc
from aiostream import stream
from grpc import aio

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as legacy_offers_pb2,
)
from snowfall.project.junction.provider import repository
from snowfall.project.junction.provider.v1 import offers_pb2, offers_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.transport.grpc import service

_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
SimpleSearchCriteriaTaskGenerator = Callable[
    [legacy_offers_pb2.SimpleTripOfferSearch],
    list[_SearchCriteria],
]
SimpleSearchCriteriaGenerator = Callable[[_SearchCriteria], _SearchCriteria]
OfferGroupGenerator = Callable[
    [_SearchCriteria],
    AsyncIterator[legacy_offers_pb2.OfferGroup],
]
_DEFAULT_ALLOWED_WINDOW_TD = datetime.timedelta(minutes=0)


@dataclasses.dataclass(frozen=True)
class SimpleOfferSearchImplementation(Generic[_SearchCriteria]):
    search_criteria_task_generator: SimpleSearchCriteriaTaskGenerator[_SearchCriteria]
    search_criteria_generator: SimpleSearchCriteriaGenerator[_SearchCriteria]
    offer_group_cache_key_generator: repository.CacheKeyGenerator[_SearchCriteria]
    offer_group_generator: repository.OfferGroupGenerator[_SearchCriteria]
    allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD


class SimpleOfferSearcher(Generic[_SearchCriteria]):
    _search_timeout_s = 50  # noqa: WPS432

    def __init__(
        self,
        task_generator: SimpleSearchCriteriaTaskGenerator[_SearchCriteria],
        criteria_generator: SimpleSearchCriteriaGenerator[_SearchCriteria],
        offer_group_repository: repository.OfferGroupRepository[_SearchCriteria],
        allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD,
    ):
        self._allowed_window_td = allowed_window_td
        self._offer_group_repository = offer_group_repository
        self._search_criteria_task_generator = task_generator
        self._search_criteria_generator = criteria_generator
        self._logger = stdout.get_logger()

    @classmethod
    def from_implementation(
        cls,
        implementation: SimpleOfferSearchImplementation[_SearchCriteria],
        redis_client: redis.Client[bytes],
    ) -> SimpleOfferSearcher[_SearchCriteria]:
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
        search: legacy_offers_pb2.SimpleTripOfferSearch,
    ) -> AsyncIterator[legacy_offers_pb2.OfferGroup]:
        search_criterion_tasks = self._search_criteria_task_generator(search)
        generators = [
            self._process_simple_search_task(search_criterion_task)
            for search_criterion_task in search_criterion_tasks
        ]

        if not generators:
            return

        async with stream.merge(*generators).stream() as offer_groups:
            async for offer_group in offer_groups:
                yield offer_group

    async def _process_simple_search_task(
        self,
        task: _SearchCriteria,
    ) -> AsyncIterator[legacy_offers_pb2.OfferGroup]:
        search_criteria = self._search_criteria_generator(task)
        offer_groups = self._offer_group_repository.find(search_criteria)
        try:
            # Timeout and return here, so if there are completed tasks in .search()
            # it can still return a partial result.
            async with asyncio.timeout(self._search_timeout_s):
                async for offer_group in offer_groups:
                    yield offer_group
        except TimeoutError:
            self._logger.warning("Offer group matches timed out.")


class SimpleSearchService(service.Service, offers_pb2_grpc.SimpleOfferServiceServicer):
    def __init__(
        self,
        simple_offer_searcher: SimpleOfferSearcher[_SearchCriteria],
        enabled_resellers: Sequence[str],
        provider_company_id: str,
        provider_name: str,
    ):
        self._enabled_resellers = enabled_resellers
        self._provider_company_id = provider_company_id
        self._provider_name = provider_name
        self._simple_offer_searcher = simple_offer_searcher

    def get_name(self) -> str:
        return offers_pb2.DESCRIPTOR.services_by_name["SimpleOfferService"].full_name

    def register(self, server: aio.Server) -> None:
        offers_pb2_grpc.add_SimpleOfferServiceServicer_to_server(self, server)

    async def SimpleSearchOffers(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.SimpleSearchOffersRequest,
        context: aio.ServicerContext,
    ) -> offers_pb2.SimpleSearchOffersResponse:
        if request.WhichOneof("offer_search_task") != "simple_offer_search_task":
            return offers_pb2.SimpleSearchOffersResponse()

        if request.simple_offer_search_task.reseller_id not in self._enabled_resellers:
            return offers_pb2.SimpleSearchOffersResponse()

        return offers_pb2.SimpleSearchOffersResponse(
            trip_offer_search_results=offers_pb2.TripOfferSearchResults(
                results=[
                    offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=request.simple_offer_search_task.offer_search_id,
                        offer=offer_group,
                        provider_company_id=self._provider_company_id,
                        provider_name=self._provider_name,
                    )
                    async for offer_group in self._simple_offer_searcher.search(
                        request.simple_offer_search_task.search,
                    )
                ],
            ),
        )


class SimpleOfferSearchConsumer(Generic[_SearchCriteria]):
    def __init__(
        self,
        consumer: amqp_consumer.Consumer[offers_amqp_pb2.SimpleTripOfferSearchTask],
        producer: amqp_producer.Producer,
        simple_offer_searcher: SimpleOfferSearcher[_SearchCriteria],
        pay_company_id: str,
        provider_name: str,
        provider_id: str,
        reseller_providers: Mapping[str, Sequence[str]],
    ):
        self._consumer = consumer
        self._producer = producer
        self._simple_offer_searcher = simple_offer_searcher
        self._pay_company_id = pay_company_id
        self._provider_name = provider_name
        self._provider_id = provider_id
        self._reseller_providers = reseller_providers

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.SimpleTripOfferSearchTask],
    ) -> None:
        if self._provider_blocked_for_reseller(amqp_message.body.reseller_id):
            return

        await self._publish_simple_offer_search_results(amqp_message)

    def _provider_blocked_for_reseller(self, reseller_id: str) -> bool:
        return self._provider_id not in self._reseller_providers.get(reseller_id, [])

    async def _publish_simple_offer_search_results(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.SimpleTripOfferSearchTask],
    ) -> None:
        offer_groups = self._simple_offer_searcher.search(
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


def create_trip_offer_search_consumer(
    amqp_connection: abc.AbstractConnection,
    redis_client: redis.Client[bytes],
    implementation: SimpleOfferSearchImplementation[_SearchCriteria],
    app_name: str,
    pay_company_id: str,
    provider_name: str,
    provider_id: str,
    reseller_providers: Mapping[str, Sequence[str]],
) -> SimpleOfferSearchConsumer[_SearchCriteria]:
    producer = amqp_producer.Producer(
        connection=amqp_connection,
        exchange=amqp_types.Exchange("offers"),
    )

    return SimpleOfferSearchConsumer(
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
        simple_offer_searcher=SimpleOfferSearcher.from_implementation(
            implementation=implementation,
            redis_client=redis_client,
        ),
        pay_company_id=pay_company_id,
        provider_name=provider_name,
        provider_id=provider_id,
        reseller_providers=reseller_providers,
    )
