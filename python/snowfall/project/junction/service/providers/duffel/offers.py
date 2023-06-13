from __future__ import annotations

import contextlib
from typing import Any, cast

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports, offers, service
from snowfall.project.junction.service.providers.duffel import cache, config, criteria
from snowfall.project.junction.service.providers.duffel.search import adapter
from snowfall.project.junction.service.providers.duffel.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    offer_request.OfferRequestData,
]


async def offers_factory(
    app: service.Application[config.Settings],
    amqp_connection: types.Connection,
    redis_connection: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = await stack.enter_async_context(
        RateLimitClient(
            app.settings.rate_limiter_grpc_host,
            app.settings.rate_limiter_service_configs.get("duffel"),
        ),
    )

    duffel_client = client.DuffelClient(
        api_base_url=app.settings.api_base_url,
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )
    duffle_adapter = adapter.DuffelSearchAdapter(
        duffel_client=duffel_client,
        offers_cache=cache.OfferCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        ),
        ttl=app.settings.ttl,
        enabled_airlines=frozenset(app.settings.enabled_airlines),
        disabled_airlines=frozenset(app.settings.disabled_airlines),
    )
    airport_mapping = airports.AirportRepository(
        airports_data=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(
                "snowfall.project.junction.service.providers.duffel.main",
            ).load("airports.json"),
        ),
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
    )
