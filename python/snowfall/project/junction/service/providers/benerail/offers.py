from __future__ import annotations

import contextlib
import random

import httpx
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import cabin_classes, notifications, offers
from snowfall.project.junction.service.providers.benerail import (
    adapter,
    cache,
    config,
    criteria,
    train_stations,
)
from snowfall.project.junction.service.providers.benerail.v1alpha import amqp_pb2
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.benerail import client

_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    criteria.SearchCriteria,
]


async def offers_app(
    app: service.Application[config.Settings],
    amqp_conn: types.Connection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    stations = await train_stations.load_train_stations()
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )

    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            timeout=app.settings.api_timeout.seconds,
            cert=config.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=app.settings.api_base_url,
        http_client=http_client,
    )

    benerail_adapter = adapter.BenerailAdapter(
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
        notifier=notifications.LogNotifier(),
        notifications_producer=producer.Producer(
            amqp_conn,
            types.Exchange("notifications"),
        ),
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                mapping=stations,
                resolution=8,
            ),
        ).from_search,
        search_criteria_generator=criteria.SearchCriteriaGenerator(
            train_station_repository=train_stations.TrainStationRepository(
                train_stations=stations,
            ),
        ).from_search_criteria_task,
        offer_group_cache_key_generator=cache.generate_cache_key,
        offer_group_generator=benerail_adapter.gather_search_results,
    )
