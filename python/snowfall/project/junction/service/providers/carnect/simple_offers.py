from __future__ import annotations

import contextlib

from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.provider import simple_offers
from snowfall.project.junction.service.providers.carnect import (
    adapter,
    cache,
    config,
    criteria,
)
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application, httpx_factory
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings

_Impl = simple_offers.SimpleOfferSearchImplementation[amqp_pb2.Criteria]


async def simple_search_app(
    app: application.Application[config.Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)

    carnect_config = carnect_settings.Config(
        timeout=app.settings.ttl.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=http_client,
        config=carnect_config,
    )
    carnect_adapter = adapter.CarnectOffersAdapter(
        carnect_client=carnect_client,
        carnect_config=carnect_config,
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_conn, prefix=app.name),
        ),
        ttl=app.settings.ttl,
    )

    return simple_offers.SimpleOfferSearchImplementation(
        search_criteria_task_generator=criteria.simple_search_criteria_task_generator,
        search_criteria_generator=criteria.simple_search_criteria_generator,
        offer_group_cache_key_generator=cache.generate_cache_key,
        offer_group_generator=carnect_adapter.gather_offer_groups,
    )
