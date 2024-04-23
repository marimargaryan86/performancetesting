from __future__ import annotations

import base64
import datetime
import random
import tempfile

import httpx
import pydantic
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    cabin_classes,
    meta,
    searches,
    service,
)
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.benerail import (
    adapter,
    cache,
    pricing,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    PROVIDER_ID,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.benerail import client

_PROVIDER_NAME = "Benerail"


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    storage_dsn: service.AnyDsn
    mongo_dsn: tuple[pydantic.AnyUrl]
    subscription_key: str
    api_base_url: pydantic.AnyUrl
    cert_base64: str


class _PricingSettings(service.ProviderSettings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    cert_base64: str
    subscription_key: str
    api_base_url: pydantic.AnyUrl


def cert_tmp_path(cert_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(cert_base64))

        return tmp_file.name


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(rail=True),
    )


async def _pricing(app: service.Application[_PricingSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            cert=cert_tmp_path(app.settings.cert_base64),
        ),
    )
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )

    quote_task_consumer = pricing.QuoteTaskConsumer(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_pricing_consumer".format(app.name),
            binds=[(types.Exchange("searches"), "searches.pricing")],
        ),
        quote_result_producer=pricing.QuoteResultProducer(
            producer_obj=producer.Producer(connection, types.Exchange("searches")),
            routing_key="searches.pricing_results",
        ),
        search_result_cache=cache.OffersCache(client=redis_client),
        quote_cache=cache.QuoteCache(
            client=redis_client,
        ),
        benerail_adapter=adapter.BenerailAdapter(benerail_client),
        client=benerail_client,
        ttl=app.settings.ttl,
    )

    await quote_task_consumer.consume()


async def _search_factory(
    app: service.Application[_Settings],
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
            cert=cert_tmp_path(app.settings.cert_base64),
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
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.CriteriaGenerator().criteria_task_generator,
        search_result_cache_key_generator=provider_searches.cache_key,
        search_result_generator=benerail_adapter.gather_search_results,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="junction-rocket-providers-benerail",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_pricing,
            settings_class=_PricingSettings,
        ),
    )
