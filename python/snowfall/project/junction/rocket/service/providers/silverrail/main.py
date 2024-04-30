from __future__ import annotations

import base64
import datetime
import tempfile

import httpx
import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    meta,
    searches,
    service,
)
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.silverrail import (
    adapter,
    bookings,
    cache,
    criteria,
    pricing,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.silverrail import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.silverrail.constant import (
    PROVIDER_ID,
)
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import amqp_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.silverrail import client

_PROVIDER_NAME = "Silverrail"


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    api_base_url: pydantic.HttpUrl
    cert_base64: str
    key_base64: str
    distributor_code: str
    pos_code: str
    channel_code: str
    pay_company_id: str
    storage_dsn: service.AnyDsn


def cert_tmp_path(cert_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(cert_base64))

        return tmp_file.name


def key_tmp_path(key_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(key_base64))

        return tmp_file.name


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(rail=True),
    )


async def _bookings(
    app: service.Application[_Settings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            cert=(
                cert_tmp_path(app.settings.cert_base64),
                key_tmp_path(app.settings.key_base64),
            ),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    silverrail_client = client.SilverrailClient(
        base_url=str(app.settings.api_base_url),
        settings=client.SilverrailSettings(
            distributor_code=app.settings.distributor_code,
            pos_code=app.settings.pos_code,
            channel_code=app.settings.channel_code,
        ),
        http_client=http_client,
    )

    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    await bookings.Consumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_bookings".format(app.name),
            binds=[(types.Exchange("bookings"), "bookings.prices")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("bookings"),
        ),
        booker=bookings.Booker(
            quote_cache=cache.QuoteCache(client=redis_client),
            booking_storage=storage,
            silverrail_client=silverrail_client,
            provider_id=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ),
    ).consume()


async def _pricing(
    app: service.Application[_Settings],
) -> None:
    stations = await train_stations.load_train_stations()
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            cert=(
                cert_tmp_path(app.settings.cert_base64),
                key_tmp_path(app.settings.key_base64),
            ),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    silverrail_client = client.SilverrailClient(
        base_url=str(app.settings.api_base_url),
        settings=client.SilverrailSettings(
            distributor_code=app.settings.distributor_code,
            pos_code=app.settings.pos_code,
            channel_code=app.settings.channel_code,
        ),
        http_client=http_client,
    )
    offer_matcher = adapter.SilverrailOfferMatcher(
        silverrail_client=silverrail_client,
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=stations,
        ),
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )

    amqp_connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
    )

    quote_task_consumer = pricing.QuoteTaskConsumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_pricing_consumer".format(app.name),
            binds=[(types.Exchange("searches"), "searches.pricing")],
        ),
        quote_result_producer=pricing.QuoteResultProducer(
            producer_obj=producer.Producer(amqp_connection, types.Exchange("searches")),
            routing_key="searches.pricing_results",
        ),
        result_detail_cache=cache.ResultDetailCache(client=redis_client),
        quote_cache=cache.QuoteCache(client=redis_client),
        ttl=app.settings.ttl,
        offer_matcher=offer_matcher,
        pay_company_id=app.settings.pay_company_id,
    )

    await quote_task_consumer.consume()


async def _search_factory(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
) -> searches.SearchImplementation[criteria.Criteria]:
    stations = await train_stations.load_train_stations()

    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            cert=(
                cert_tmp_path(app.settings.cert_base64),
                key_tmp_path(app.settings.key_base64),
            ),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    silverrail_client = client.SilverrailClient(
        base_url=str(app.settings.api_base_url),
        settings=client.SilverrailSettings(
            distributor_code=app.settings.distributor_code,
            pos_code=app.settings.pos_code,
            channel_code=app.settings.channel_code,
        ),
        http_client=http_client,
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    silverrail_adapter = adapter.SilverrailOffersAdapter(
        silverrail_client=silverrail_client,
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=stations,
        ),
        ttl=app.settings.ttl,
        result_detail_cache=cache.ResultDetailCache(
            client=redis_client,
        ),
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                mapping=stations,
                resolution=8,
            ),
        ).criteria_task_generator,
        search_result_cache_key_generator=cache.generate_cache_key,
        search_result_generator=silverrail_adapter.gather_search_results,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="junction-rocket-providers-silverrail",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_pricing,
            settings_class=_Settings,
        ),
        service.Command(
            name="bookings",
            callback=_bookings,
            settings_class=_Settings,
        ),
    )
