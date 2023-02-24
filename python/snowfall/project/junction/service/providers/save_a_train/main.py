from __future__ import annotations

import contextlib
import datetime
import json
import os
import pathlib
import pkgutil
import random
from typing import Sequence, cast

import aiosmtplib
import httpx
import pydantic
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    cabin_classes,
    notifications,
    offers,
    repository,
)
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    consumer,
    criteria,
    train_stations,
)
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.stdlib.transport.grpc import client as grpc_client
from snowfall.vendor.save_a_train import client
from snowfall.vendor.save_a_train.models import request as request_models

_OFFERS = "offers"


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
    geodata_address: Sequence[str]
    output_file: str = pydantic.Field(hidden=True, argument=True)


class _OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _SearchSettings(_SatConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    mongo_dsn: tuple[pydantic.AnyUrl]
    allowed_window_td: datetime.timedelta = datetime.timedelta(minutes=10)


class _OrdersSettings(_SatConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    mongo_dsn: tuple[pydantic.AnyUrl]


class _NotificationsSettings(_SatConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    mongo_dsn: tuple[pydantic.AnyUrl]


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_conn: aioredis.Redis[str] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
        )
        connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        trip_search_consumer = offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client(redis_conn, prefix=app.name),
            criteria_generator=criteria.CriteriaGenerator(
                h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                    mapping=await _load_train_stations(),
                    resolution=8,
                ),
            ).from_search_task,
            internal_exchange_name=app.name,
        )

        await trip_search_consumer.consume()


async def _searches(app: service.Application[_SearchSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
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
        sat_adapter = adapter.SaveATrainAdapter(
            save_a_train_client=save_a_train_client,
            train_station_repository=train_stations.TrainStationRepository(
                train_stations=await _load_train_stations(),
            ),
            provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
                mongo.sat.provider_cabin_mapping,
            ),
            offers_cache=cache.OffersCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
            notifier=notifications.LogNotifier(),
            notifications_producer=producer.Producer(
                amqp_connection,
                types.Exchange("notifications"),
            ),
        )
        search_consumer = offers.SearchCriteriaConsumer[
            amqp_pb2.SearchCriteriaTask,
            request_models.CreateSearchRequest,
        ](
            search_criteria_generator_func=sat_adapter.search_criteria_generator,
            consumer=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("save_a_train"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("save_a_train"),
                            ),
                        ),
                    ).execute,
                ],
            ),
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange(_OFFERS),
            ),
            offer_group_repository=repository.OfferGroupRepository(
                redis=redis.Client(
                    redis=redis_connection,
                    prefix=app.name,
                ),
                offer_group_cache_key_func=sat_adapter.generate_cache_key,
                offer_group_generator=sat_adapter.gather_search_results,
            ),
            allowed_window_td=app.settings.allowed_window_td,
        )

        await search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
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
            ),
            offers_cache=offer_cache,
        )

        await orders_consumer.consume()


async def _price_quotes(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
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
        ).consume()


async def _notifications(app: service.Application[_NotificationsSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
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
        )
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
        channel = await stack.enter_async_context(
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

        await notifications_consumer.consume()


async def _dump_stations(app: service.Application[_DumpStationsSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
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
        geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
            grpc_client.create_channel(
                random.choice(app.settings.geodata_address),  # nosec
            ),
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
    entrypoint = service.Entrypoint(name="save_a_train")

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=_dump_stations,
            settings_class=_DumpStationsSettings,
        ),
        service.Command(
            name=_OFFERS,
            callback=_offers,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="searches",
            callback=_searches,
            settings_class=_SearchSettings,
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
            settings_class=_OffersSettings,
        ),
    )
