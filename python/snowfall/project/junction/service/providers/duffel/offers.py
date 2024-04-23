from __future__ import annotations

from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports, offers, service
from snowfall.project.junction.service.providers.duffel import cache, config, criteria
from snowfall.project.junction.service.providers.duffel.client_factory import (
    DuffelClientFactory,
)
from snowfall.project.junction.service.providers.duffel.search import adapter
from snowfall.project.junction.service.providers.duffel.v1 import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import grpc_factory, httpx_factory
from snowfall.vendor.rate_limiter import gubernator_pb2_grpc
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    adapter.SearchCriteriaWrapper,
]


async def offers_factory(
    app: service.Application[config.Settings],
    amqp_connection: abc.AbstractConnection,
    redis_connection: aioredis.Redis[bytes],
) -> _Impl:
    http_client = await httpx_factory.make_client(
        app,
        timeout=app.settings.http_timeout,
    )
    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["duffel"],
    )
    offer_client_factory = DuffelClientFactory(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
        resellers_map=app.settings.resellers_map,
    )
    duffle_adapter = adapter.DuffelSearchAdapter(
        resellers_map=app.settings.resellers_map,
        duffel_client_factory=offer_client_factory,
        offers_cache=cache.OfferCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        ),
        ttl=app.settings.ttl,
        enabled_airlines=frozenset(app.settings.enabled_airlines),
        disabled_airlines=frozenset(app.settings.disabled_airlines),
    )
    airport_mapping = airports.AirportRepository(
        airports_data=filesystem.PkgLoader("snowfall.data").load("airports.json"),
    ).all_()

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[airports.Airport](
                mapping=airport_mapping,
                resolution=7,
            ),
        ).from_search,
        search_criteria_generator=duffle_adapter.search_criteria_generator,
        offer_group_cache_key_generator=duffle_adapter.generate_cache_key,
        offer_group_generator=duffle_adapter.gather_search_results,
        allowed_window_td=app.settings.allowed_window_td,
    )
