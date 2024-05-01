from __future__ import annotations

import random

import httpx
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    cabin_classes,
    searches,
    service,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    adapter,
    cache,
    helper_functions,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.benerail.config import (
    Settings,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.benerail import client


async def search_factory(
    app: service.Application[Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
) -> searches.SearchImplementation[provider_searches.Criteria]:
    stations = await train_stations.load_train_stations()
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            cert=helper_functions.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )

    benerail_adapter = adapter.BenerailOffersAdapter(
        benerail_client=benerail_client,
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=stations,
        ),
        provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
            mongo.benerail.provider_cabin_mapping,
        ),
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_conn, prefix=app.name),
        ),
        ttl=app.settings.ttl,
        pay_company_id=app.settings.pay_company_id,
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.CriteriaGenerator().criteria_task_generator,
        search_result_cache_key_generator=provider_searches.cache_key,
        search_result_generator=benerail_adapter.gather_search_results,
    )
