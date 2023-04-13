from __future__ import annotations

import contextlib
from typing import Any, cast

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports
from snowfall.project.junction.provider import offers_v2 as offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.ba_ndc import cache, config, criteria
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.models import request_offer_search_schemas

_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    request_offer_search_schemas.OfferSearchRequest,
]


async def offers_factory(
    app: service.Application[config.OffersSettings],
    amqp_connection: types.Connection,
    redis_connection: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    airport_repository = airports.AirportRepository(
        airports_data=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(
                "snowfall.project.junction.service.providers.ba_ndc.main",
            ).load("airports.json"),
        ),
    )
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    ba_ndc_client = client.BaNdcClient(
        api_base_url=app.settings.api_base_url,
        api_key=app.settings.api_key,
        http_client=http_client,
    )
    ba_ndc_adapter = adapter.BaNdcSearchAdapter(
        ba_ndc_client=ba_ndc_client,
        airport_repository=airport_repository,
        offers_cache=cache.OfferCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        ),
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[airports.Airport](
                mapping=airport_repository.all_(),
                resolution=7,
            ),
        ).from_search,
        search_criteria_generator=ba_ndc_adapter.search_criteria_generator,
        offer_group_cache_key_generator=ba_ndc_adapter.generate_cache_key,
        offer_group_generator=ba_ndc_adapter.gather_search_results,
    )
