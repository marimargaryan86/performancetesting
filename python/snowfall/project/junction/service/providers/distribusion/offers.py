from __future__ import annotations

import contextlib
import datetime

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers, service
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    config,
    criteria,
    stations,
)
from snowfall.project.junction.service.providers.distribusion.search import adapter
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models import criterias

_OFFERS = "offers"


class OffersSettings(service.OffersSettings, config.DistribusionConfig):
    ttl: datetime.timedelta = datetime.timedelta(minutes=config.DEFAULT_TTL_IN_MINUTES)
    reseller_providers: dict[str, list[str]] = {}


_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    criterias.FindConnectionsCriteria,
]


async def offers_factory(
    app: service.Application[OffersSettings],
    amqp_connection: types.Connection,
    redis_connection: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)

    distribusion_client = client.DistribusionClient(
        api_base_url=app.settings.api_base_url,
        api_key=app.settings.api_key,
        retailer_partner_number=app.settings.retailer_partner_number,
        http_client=http_client,
    )
    distribusion_adapter = adapter.DistribusionSearchAdapter(
        distribusion_client=distribusion_client,
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
        ttl=app.settings.ttl,
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[stations.Station](
                mapping=await stations.load_stations(),
                resolution=8,
            ),
        ).from_search,
        search_criteria_generator=distribusion_adapter.search_criteria_generator,
        offer_group_cache_key_generator=distribusion_adapter.generate_cache_key,
        offer_group_generator=distribusion_adapter.gather_search_results,
    )
