import random

import httpx
from motor import motor_asyncio

from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.service.providers.benerail import (
    adapter,
    cache,
    config,
    consumer,
    train_stations,
)
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.amqp import consumer as std_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.vendor.benerail import client


async def simple_search(
    app: application.Application[config.SimpleSearchSettings],
) -> None:
    stations = await train_stations.load_train_stations()
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            timeout=app.settings.api_timeout.seconds,
            cert=config.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    logging.register(http_client)
    metrics.register(http_client)
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )
    await consumer.SimpleSearchConsumer(
        consumer_obj=std_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_searches".format(app.name),
            binds=[(types.Exchange("offers"), "offers.search.trip")],
            middleware_stack=[
                trackable.ReportingMiddleware(
                    status_reporter=trackable.StatusReporter(
                        producer=producer.Producer(
                            connection=amqp_connection,
                            exchange=types.Exchange("benerail"),
                        ),
                    ),
                ).execute,
            ],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("offers"),
        ),
        benerail_offers_adapter=adapter.BenerailOffersAdapter(
            benerail_client=benerail_client,
            train_station_repository=train_stations.TrainStationRepository(
                train_stations=stations,
            ),
            provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
                mongo.benerail.provider_cabin_mapping,
            ),
            offers_cache=cache.OffersCache(
                client=redis_client,
            ),
            ttl=app.settings.ttl,
        ),
        h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
            mapping=stations,
            resolution=8,
        ),
        provider_company_id=app.settings.provider_company_id,
    ).consume()
