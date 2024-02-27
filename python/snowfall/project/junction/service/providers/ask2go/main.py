from __future__ import annotations

import contextlib
import datetime
import pathlib
import random
import zoneinfo
from collections.abc import Sequence

import aiosmtplib
import httpx
import pydantic
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    airports,
    bookings,
    cabin_classes,
    meta,
    notifications,
    offers,
    service,
    simple_offers,
)
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    consumer,
    criteria,
    notifications_service,
    pricing,
    search,
    stations,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go import offers as a2g_offers
from snowfall.project.junction.service.providers.ask2go.constant import PROVIDER_ID
from snowfall.project.junction.service.providers.ask2go.location_repository import (
    LocationRepository,
)
from snowfall.project.junction.service.providers.ask2go.train_stations import (
    ASK2GO_RESOURCE,
    ASK2GO_STATIONS_PACKAGE,
    TrainStation,
    TrainStationRepository,
)
from snowfall.project.junction.service.providers.ask2go.v1 import amqp_pb2
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, grpc_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import search as search_models
from snowfall.vendor.rate_limiter import gubernator_pb2_grpc
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient
from snowfall.vendor.rate_limiter.config import RateLimitConfig


class _OrdersSettings(service.Settings):
    amqp_dsn: pydantic.AmqpDsn
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: pydantic.RedisDsn
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    http_timeout: float = 60.0
    override_double_booking_check: bool = False
    storage_dsn: service.AnyDsn


class _Settings(service.ProviderSettings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1
    mongo_dsn: Sequence[pydantic.AnyUrl]
    reseller_affiliate_mapping: dict[str, str] = pydantic.Field(default_factory=dict)
    storage_dsn: service.AnyDsn
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]
    min_lower_bound: datetime.timedelta = datetime.timedelta(hours=24)


class _PriceQuotesSettings(service.PriceQuoteSettings):
    amqp_dsn: pydantic.AmqpDsn
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1
    mongo_dsn: Sequence[pydantic.AnyUrl]
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]


class _SeatMapsSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: pydantic.RedisDsn
    amqp_dsn: pydantic.AmqpDsn
    http_timeout: float = 60.0


class _OrderChangesSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    queue_name: str
    endpoint_url: str
    a2g_sqs_aws_access_key_id: str
    a2g_sqs_aws_secret_access_key: str
    aws_region: str
    wait_time_between_polling: int = 20
    http_timeout: float = 60.0


_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    search_models.CreateSearchCriteria,
]


class DumpStationsSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    geodata_address: str
    output_dir: pydantic.DirectoryPath = pathlib.Path()
    http_timeout: float = 60.0


_PROVIDER_NAME = "Ask2Go"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=PROVIDER_ID, name=_PROVIDER_NAME)


async def _dump_stations(
    app: service.Application[DumpStationsSettings],
) -> None:
    settings = app.settings

    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
    ) as http_client:
        logging.register(http_client)
        metrics.register(http_client)
        ask2go_client = client.Ask2GoClient(
            api_base_url=str(app.settings.api_base_url),
            api_booking_base_url=str(app.settings.api_booking_base_url),
            http_client=http_client,
        )

        geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
            await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
        )
        output_file_path = "/".join(
            [
                str(settings.output_dir),
                "ask2go_stations.json",
            ],
        )
        await stations.dump_stations(geocoder, ask2go_client, output_file_path)


async def _offers(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ask2go"],
    )

    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )
    airport_repo = airports.AirportRepository(
        airports_data=filesystem.PkgLoader("snowfall.data").load("airports.json"),
    )
    json_data = filesystem.PkgLoader(ASK2GO_STATIONS_PACKAGE).load(
        ASK2GO_RESOURCE,
    )
    train_station_repo = TrainStationRepository([
        TrainStation(**{**data, "timezone": zoneinfo.ZoneInfo(data["timezone"])})
        for data in json_data
    ])
    location_repository = LocationRepository(airport_repo, train_station_repo)
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[airports.Airport](
                mapping=airport_repo.all_(),
                resolution=7,
            ),
            stations_h3_mapping=h3.H3MappingRepository[TrainStation](
                mapping=train_station_repo.all_(),
                resolution=7,
            ),
            reseller_id_affiliate_id_map=app.settings.reseller_affiliate_mapping,
            min_lower_bound=app.settings.min_lower_bound,
        ).from_search,
        search_criteria_generator=search.search_criteria_generator,
        offer_group_cache_key_generator=search.generate_cache_key,
        offer_group_generator=a2g_offers.offer_group_generator(
            a2g_adapter=search.Adapter(ask2go_client=ask2go_client),
            a2g_transformer=transformer.OfferTransformer(
                repository=location_repository,
                cabin_mapping_repository=cabin_classes.CabinMappingRepository(
                    mongo.ask2go.provider_cabin_mapping,
                ),
                offer_cache=cache.OfferCache(
                    client=redis.Client[bytes](
                        redis_conn,
                        prefix=app.name,
                    ),
                ),
                price_cache=cache.PriceQuoteCache(
                    client=redis.Client[bytes](
                        redis_conn,
                        prefix=app.name,
                    ),
                ),
                offer_ttl=app.settings.ttl,
            ),
        ),
    )


def simple_criteria_generator(
    search_criteria: search_models.CreateSearchCriteria,
) -> search_models.CreateSearchCriteria:
    return search_criteria


async def _simple_offers(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> simple_offers.SimpleOfferSearchImplementation[search_models.CreateSearchCriteria]:
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)

    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ask2go"],
    )

    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )

    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    airport_repo = airports.AirportRepository(
        airports_data=filesystem.PkgLoader("snowfall.data").load("airports.json"),
    )
    json_data = filesystem.PkgLoader(ASK2GO_STATIONS_PACKAGE).load(
        ASK2GO_RESOURCE,
    )
    train_station_repo = TrainStationRepository([
        TrainStation(**{**data, "timezone": zoneinfo.ZoneInfo(data["timezone"])})
        for data in json_data
    ])
    location_repository = LocationRepository(airport_repo, train_station_repo)

    offer_group_generator = a2g_offers.offer_group_generator(
        a2g_adapter=search.Adapter(ask2go_client=ask2go_client),
        a2g_transformer=transformer.OfferTransformer(
            repository=location_repository,
            cabin_mapping_repository=cabin_classes.CabinMappingRepository(
                mongo.ask2go.provider_cabin_mapping,
            ),
            offer_cache=cache.OfferCache(
                client=redis.Client[bytes](
                    redis_conn,
                    prefix=app.name,
                ),
            ),
            price_cache=cache.PriceQuoteCache(
                client=redis.Client[bytes](
                    redis_conn,
                    prefix=app.name,
                ),
            ),
            offer_ttl=app.settings.ttl,
        ),
    )

    search_criteria_task_generator = criteria.CriteriaGenerator(
        h3_mapping=h3.H3MappingRepository[airports.Airport](
            mapping=airport_repo.all_(),
            resolution=7,
        ),
        stations_h3_mapping=h3.H3MappingRepository[TrainStation](
            mapping=train_station_repo.all_(),
            resolution=7,
        ),
        reseller_id_affiliate_id_map=app.settings.reseller_affiliate_mapping,
        min_lower_bound=app.settings.min_lower_bound,
    ).criteria_generator

    return simple_offers.SimpleOfferSearchImplementation(
        search_criteria_task_generator=search_criteria_task_generator,
        search_criteria_generator=simple_criteria_generator,
        offer_group_cache_key_generator=search.generate_cache_key,
        offer_group_generator=offer_group_generator,
    )


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
        fake_the_bookings=app.environment != "production",
    )
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    await consumer.OrderConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booking_handler=booking.BookingHandler(
            ask2go_client=ask2go_client,
            notifier=notifications.SmtpNotifier(
                smtp_client=aiosmtplib.SMTP(
                    hostname=app.settings.smtp_dsn.host,
                    port=int(app.settings.smtp_dsn.port or 0) or None,
                    username=app.settings.smtp_dsn.username,
                    password=app.settings.smtp_dsn.password,
                    start_tls=True,
                ),
                sender=app.settings.smtp_sender,
                recipient=app.settings.smtp_recipient,
            ),
            booking_storage=storage,
            override_double_booking_check=app.settings.override_double_booking_check,
            offer_cache=cache.OfferCache(client=redis_client),
        ),
        price_quote_cache=cache.PriceQuoteCache(
            client=redis_client,
        ),
        provider_id=PROVIDER_ID,
        provider_name=_PROVIDER_NAME,
    ).consume()


async def _order_changes(app: service.Application[_OrderChangesSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)

    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
    )

    await notifications_service.NotificationsServiceConsumer(
        ask2go_client=ask2go_client,
        poll_interval=app.settings.wait_time_between_polling,
    ).start_listening(
        queue_name=app.settings.queue_name,
        endpoint_url=app.settings.endpoint_url,
        aws_access_key_id=app.settings.a2g_sqs_aws_access_key_id,
        aws_secret_access_key=app.settings.a2g_sqs_aws_secret_access_key,
        region=app.settings.aws_region,
    )


async def _price_quotes(app: service.Application[_PriceQuotesSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ask2go"],
    )

    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )

    airport_repo = airports.AirportRepository(
        airports_data=filesystem.PkgLoader("snowfall.data").load("airports.json"),
    )
    json_data = filesystem.PkgLoader(ASK2GO_STATIONS_PACKAGE).load(
        ASK2GO_RESOURCE,
    )
    train_station_repo = TrainStationRepository([
        TrainStation(**{**data, "timezone": zoneinfo.ZoneInfo(data["timezone"])})
        for data in json_data
    ])
    location_repository = LocationRepository(airport_repo, train_station_repo)

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
        offer_cache=cache.OfferCache(
            client=redis_client,
        ),
        offer_transformer=transformer.OfferTransformer(
            repository=location_repository,
            cabin_mapping_repository=cabin_classes.CabinMappingRepository(
                mongo.ask2go.provider_cabin_mapping,
            ),
            offer_cache=cache.OfferCache(
                client=redis_client,
            ),
            price_cache=cache.PriceQuoteCache(
                client=redis_client,
            ),
            offer_ttl=app.settings.ttl,
        ),
        pricing_adapter=pricing.Adapter(
            ask2go_client=ask2go_client,
            poll_retries_limit=app.settings.poll_retries_limit,
            wait_time_between_polling=app.settings.wait_time_between_polling,
        ),
        provider_company_id=app.settings.provider_company_id,
    ).consume()


async def _seat_maps(app: service.Application[_SeatMapsSettings]) -> None:
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    ask2go_client = client.Ask2GoClient(
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        http_client=http_client,
    )
    await consumer.SeatMapRpcServer(
        address=str(app.settings.amqp_dsn),
        exchange=types.Exchange("seat_maps"),
        queue_name="{0}_seat_maps".format(app.name),
        routing_key="seat.maps",
        ask2go_client=ask2go_client,
        offer_cache=cache.OfferCache(
            client=redis_client,
        ),
    ).consume()


async def _bookings_factory(
    app: service.Application[_Settings],
) -> bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    return bookings.Implementation(
        storage=storage,
        transformer=booking.Transformer(
            provider_identifier=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ).raw_to_booking,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="ask2go",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        offers_factory=_offers,
        bookings_factory=_bookings_factory,
        simple_offers_factory=_simple_offers,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=_dump_stations,
            settings_class=DumpStationsSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_PriceQuotesSettings,
        ),
        service.Command(
            name="seat-maps",
            callback=_seat_maps,
            settings_class=_SeatMapsSettings,
        ),
        service.Command(
            name="order-changes",
            callback=_order_changes,
            settings_class=_OrderChangesSettings,
        ),
    )
