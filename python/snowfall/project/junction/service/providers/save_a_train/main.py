from __future__ import annotations

import contextlib
import datetime
import json
import os
import pathlib
import pkgutil
import random
import uuid
from collections.abc import Sequence
from typing import cast

import aiosmtplib
import httpx
import pydantic
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    bookings,
    cabin_classes,
    meta,
    notifications,
    offers,
    service,
)
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    consumer,
    criteria,
    train_stations,
)
from snowfall.project.junction.service.providers.save_a_train.v1 import amqp_pb2
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.stdlib.transport.grpc import client as grpc_client
from snowfall.vendor.save_a_train import client
from snowfall.vendor.save_a_train.models import request

_PROVIDER_ID = uuid.UUID("a5547dae-9c65-4746-8637-d0601865508e")
_PROVIDER_NAME = "Save A Train"


class _SatConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_email: str
    api_password: str
    api_timeout: int = 40
    api_search_base_url: pydantic.AnyUrl
    api_search_timeout: int = 1
    api_search_requests_limit: int = 40
    api_search_password: str
    api_booking_token: str


class _DumpStationsSettings(_SatConfig, service.Settings):
    geodata_address: str
    output_file: str = pydantic.Field(hidden=True, argument=True)


class _Settings(_SatConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    mongo_dsn: tuple[pydantic.AnyUrl]
    allowed_window_td: datetime.timedelta = datetime.timedelta(minutes=0)
    storage_dsn: service.AnyDsn


class _PriceQuoteSettings(service.PriceQuoteSettings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _OrdersSettings(_SatConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    mongo_dsn: tuple[pydantic.AnyUrl]
    storage_dsn: service.AnyDsn


class _NotificationsSettings(_SatConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    mongo_dsn: tuple[pydantic.AnyUrl]
    storage_dsn: service.AnyDsn


_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    request.CreateSearchRequest,
]


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


async def _offers_factory(
    app: service.Application[_Settings],
    amqp_conn: types.Connection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    stations = await _load_train_stations()
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    save_a_train_client = client.SATClient(
        email=app.settings.api_email,
        password=app.settings.api_password,
        password_search=app.settings.api_search_password,
        token=app.settings.api_booking_token,
        api_url=app.settings.api_base_url,
        api_search_url=app.settings.api_search_base_url,
        api_search_timeout=app.settings.api_search_timeout,
        api_search_requests_limit=app.settings.api_search_requests_limit,
        client=http_client,
    )
    booking_storage = await stack.enter_async_context(
        filesystem.Storage.from_dsn(app.settings.storage_dsn),
    )
    # TODO: do we need to call get_token on the save_a_train_client?
    sat_adapter = adapter.SaveATrainAdapter(
        save_a_train_client=save_a_train_client,
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=stations,
        ),
        provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
            mongo.sat.provider_cabin_mapping,
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
        booking_storage=booking_storage,
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                mapping=stations,
                resolution=8,
            ),
        ).from_search,
        search_criteria_generator=sat_adapter.search_criteria_generator,
        offer_group_cache_key_generator=sat_adapter.generate_cache_key,
        offer_group_generator=sat_adapter.gather_search_results,
        allowed_window_td=app.settings.allowed_window_td,
    )


async def _bookings_factory(
    app: service.AsyncApplication[_Settings],
) -> bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(app.settings.storage_dsn),
    )

    return bookings.Implementation(
        storage=storage,
        transformer=adapter.Transformer(
            provider_identifier=_PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ).raw_to_booking,
    )


async def _orders(  # noqa: WPS217
    app: service.AsyncApplication[_OrdersSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # noqa: S311
            decode_responses=False,
        ).client(),
    )

    save_a_train_client = client.SATClient(
        email=app.settings.api_email,
        password=app.settings.api_password,
        password_search=app.settings.api_search_password,
        token=app.settings.api_booking_token,
        api_url=app.settings.api_base_url,
        api_search_url=app.settings.api_search_base_url,
        api_search_timeout=app.settings.api_search_timeout,
        api_search_requests_limit=app.settings.api_search_requests_limit,
        client=http_client,
    )
    # TODO: do we need to call get_token on the save_a_train_client?
    offer_cache = cache.OffersCache(
        client=redis.Client(redis_connection, prefix=app.name),
    )
    booking_storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(app.settings.storage_dsn),
    )
    orders_consumer = consumer.OrdersConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        adapter=adapter.SaveATrainAdapter(
            save_a_train_client=save_a_train_client,
            train_station_repository=train_stations.TrainStationRepository(
                train_stations=await _load_train_stations(),
            ),
            provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
                mongo.sat.provider_cabin_mapping,
            ),
            offers_cache=offer_cache,
            ttl=app.settings.ttl,
            notifier=notifications.SmtpNotifier(
                smtp_client=aiosmtplib.SMTP(
                    hostname=app.settings.smtp_dsn.host,
                    port=int(app.settings.smtp_dsn.port or 0) or None,
                    username=app.settings.smtp_dsn.user,
                    password=app.settings.smtp_dsn.password,
                    start_tls=True,
                ),
                sender=app.settings.smtp_sender,
                recipient=app.settings.smtp_recipient,
            ),
            notifications_producer=producer.Producer(
                amqp_connection,
                types.Exchange("notifications"),
            ),
            booking_storage=booking_storage,
        ),
        offers_cache=offer_cache,
    )

    await orders_consumer.consume()


async def _price_quotes(app: service.AsyncApplication[_PriceQuoteSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # noqa: S311
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )

    await consumer.PriceQuoteConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("prices"),
        ),
        offer_cache=cache.OffersCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
        price_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
        price_ttl=app.settings.ttl,
        provider_company_id=app.settings.provider_company_id,
    ).consume()


async def _notifications(  # noqa: WPS217
    app: service.AsyncApplication[_NotificationsSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # noqa: S311
            decode_responses=False,
        ).client(),
    )
    notifier = notifications.SmtpNotifier(
        smtp_client=aiosmtplib.SMTP(
            hostname=app.settings.smtp_dsn.host,
            port=int(app.settings.smtp_dsn.port or 0) or None,
            username=app.settings.smtp_dsn.user,
            password=app.settings.smtp_dsn.password,
            start_tls=True,
        ),
        sender=app.settings.smtp_sender,
        recipient=app.settings.smtp_recipient,
    )
    booking_storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(app.settings.storage_dsn),
    )
    sat_adapter = adapter.SaveATrainAdapter(
        save_a_train_client=client.SATClient(
            email=app.settings.api_email,
            password=app.settings.api_password,
            password_search=app.settings.api_search_password,
            token=app.settings.api_booking_token,
            api_url=app.settings.api_base_url,
            api_search_url=app.settings.api_search_base_url,
            api_search_timeout=app.settings.api_search_timeout,
            api_search_requests_limit=app.settings.api_search_requests_limit,
            client=http_client,
        ),
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=await _load_train_stations(),
        ),
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
        ttl=app.settings.ttl,
        notifier=notifier,
        notifications_producer=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("notifications"),
        ),
        provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
            mongo.sat.provider_cabin_mapping,
        ),
        booking_storage=booking_storage,
    )
    await _consume_notifications(app, amqp_connection, sat_adapter, notifier)


async def _consume_notifications(
    app: service.AsyncApplication[_NotificationsSettings],
    amqp_connection: abc.AbstractConnection,
    sat_adapter: adapter.SaveATrainAdapter,
    notifier: notifications.SmtpNotifier,
) -> None:
    notifications_consumer = consumer.NotificationsConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="notifications",
            queue_arguments={
                "x-dead-letter-exchange": "notifications.retry",
                "x-dead-letter-routing-key": "notifications.retry",
            },
            binds=[(types.Exchange("notifications"), "notifications")],
        ),
        adapter=sat_adapter,
        notifier=notifier,
    )
    await _configure_queue(app, amqp_connection)
    await notifications_consumer.consume()


async def _configure_queue(
    app: service.AsyncApplication[_NotificationsSettings],
    amqp_connection: abc.AbstractConnection,
) -> None:
    channel = await app.stack.enter_async_context(
        cast(
            contextlib.AbstractAsyncContextManager[abc.AbstractChannel],
            amqp_connection.channel(),
        ),
    )
    await channel.set_qos(
        prefetch_count=((os.cpu_count() or 1) * 2) + 1,
    )
    queue = await channel.declare_queue(
        name="notifications.retry",
        durable=True,
        arguments={
            "x-message-ttl": 300000,
            "x-dead-letter-exchange": "notifications",
            "x-dead-letter-routing-key": "notifications",
        },
    )
    exchange = types.Exchange("notifications.retry")
    declared_exchange = await channel.declare_exchange(
        name=exchange.name,
        type=exchange.type_,
        durable=True,
    )
    await queue.bind(declared_exchange, "notifications.retry")


async def _dump_stations(app: service.AsyncApplication[_DumpStationsSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    save_a_train_client = client.SATClient(
        email=app.settings.api_email,
        password=app.settings.api_password,
        password_search=app.settings.api_search_password,
        token=app.settings.api_booking_token,
        api_url=app.settings.api_base_url,
        api_search_url=app.settings.api_search_base_url,
        api_search_timeout=app.settings.api_search_timeout,
        api_search_requests_limit=app.settings.api_search_requests_limit,
        client=http_client,
    )
    geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
        grpc_client.create_channel(app.settings.geodata_address),
    )

    await train_stations.dump_sat_stations(
        geocoder,
        await save_a_train_client.get_vendor_stations(),
        pathlib.Path(app.settings.output_file),
    )


async def _load_train_stations() -> list[train_stations.TrainStation]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.save_a_train.main",
        "train_stations.json",
    )

    if json_content is None:
        return []  # TODO: throw exception

    stations = json.loads(json_content.decode("utf-8"))
    return [await train_stations.make_train_station(station) for station in stations]


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="save-a-train",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        offers_factory=_offers_factory,
        bookings_factory=_bookings_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=_dump_stations,
            settings_class=_DumpStationsSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
        service.Command(
            name="notifications",
            callback=_notifications,
            settings_class=_NotificationsSettings,
        ),
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_PriceQuoteSettings,
        ),
    )
