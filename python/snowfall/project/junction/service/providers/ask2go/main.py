from __future__ import annotations

import contextlib
import datetime
import random
import uuid
from typing import Any, Sequence, cast

import aiosmtplib
import httpx
import pydantic
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    airports,
    cabin_classes,
    meta,
    notifications,
    offers,
    service,
)
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    consumer,
    criteria,
)
from snowfall.project.junction.service.providers.ask2go import offers as a2g_offers
from snowfall.project.junction.service.providers.ask2go import (
    pricing,
    search,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import search as search_models


class _OrdersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    http_timeout: float = 60.0
    override_double_booking_check: bool = False


class _Settings(service.ProviderSettings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1
    mongo_dsn: Sequence[pydantic.AnyUrl]
    reseller_affiliate_mapping: dict[str, str] = {}


class _PriceQuotesSettings(service.PriceQuoteSettings):
    amqp_dsn: pydantic.AnyUrl
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _SeatMapsSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    amqp_dsn: pydantic.AnyUrl
    http_timeout: float = 60.0


_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    search_models.CreateSearchCriteria,
]


_PROVIDER_ID = uuid.UUID("4b7d12db-7735-4c67-9645-5fc82f7c4fe8")
_PROVIDER_NAME = "Ask2Go"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


async def _offers(
    app: service.Application[_Settings],
    amqp_conn: types.Connection,
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
    ask2go_client = client.Ask2GoClient(
        api_base_url=app.settings.api_base_url,
        api_booking_base_url=app.settings.api_booking_base_url,
        http_client=http_client,
    )
    search_adapter = search.Adapter(
        ask2go_client=ask2go_client,
        poll_retries_limit=app.settings.poll_retries_limit,
    )
    airport_repo = airports.AirportRepository(
        airports_data=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(
                "snowfall.project.junction.service.providers.ask2go.main",
            ).load("airports.json"),
        ),
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[airports.Airport](
                mapping=airport_repo.all_(),
                resolution=7,
            ),
            reseller_id_affiliate_id_map=app.settings.reseller_affiliate_mapping,
        ).from_search,
        search_criteria_generator=search_adapter.search_criteria_generator,
        offer_group_cache_key_generator=search_adapter.generate_cache_key,
        offer_group_generator=a2g_offers.offer_group_generator(
            a2g_adapter=search_adapter,
            a2g_transformer=transformer.OfferTransformer(
                airport_repository=airport_repo,
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


async def _orders(app: service.AsyncApplication[_OrdersSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    ask2go_client = client.Ask2GoClient(
        api_base_url=app.settings.api_base_url,
        api_booking_base_url=app.settings.api_booking_base_url,
        http_client=http_client,
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
                    username=app.settings.smtp_dsn.user,
                    password=app.settings.smtp_dsn.password,
                    start_tls=True,
                ),
                sender=app.settings.smtp_sender,
                recipient=app.settings.smtp_recipient,
            ),
            override_double_booking_check=app.settings.override_double_booking_check,
        ),
        price_quote_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
    ).consume()


async def _price_quotes(app: service.AsyncApplication[_PriceQuotesSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    ask2go_client = client.Ask2GoClient(
        api_base_url=app.settings.api_base_url,
        api_booking_base_url=app.settings.api_booking_base_url,
        http_client=http_client,
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
        offer_cache=cache.OfferCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
        offer_transformer=transformer.OfferTransformer(
            airport_repository=airports.AirportRepository(
                airports_data=cast(
                    list[dict[str, Any]],
                    filesystem.PkgLoader(
                        "snowfall.project.junction.service.providers.ask2go.main",
                    ).load("airports.json"),
                ),
            ),
            cabin_mapping_repository=cabin_classes.CabinMappingRepository(
                mongo.ask2go.provider_cabin_mapping,
            ),
            offer_cache=cache.OfferCache(
                client=redis.Client[bytes](redis_connection, prefix=app.name),
            ),
            price_cache=cache.PriceQuoteCache(
                client=redis.Client[bytes](redis_connection, prefix=app.name),
            ),
            offer_ttl=app.settings.ttl,
        ),
        pricing_adapter=pricing.Adapter(ask2go_client=ask2go_client),
        provider_company_id=app.settings.provider_company_id,
    ).consume()


async def _seat_maps(app: service.AsyncApplication[_SeatMapsSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=False,
        ).client(),
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    ask2go_client = client.Ask2GoClient(
        api_base_url=app.settings.api_base_url,
        api_booking_base_url=app.settings.api_booking_base_url,
        http_client=http_client,
    )
    await consumer.SeatMapRpcServer(
        address=app.settings.amqp_dsn,
        exchange=types.Exchange("seat_maps"),
        queue_name="{0}_seat_maps".format(app.name),
        routing_key="seat.maps",
        ask2go_client=ask2go_client,
        offer_cache=cache.OfferCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        ),
    ).consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="ask2go",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        offers_factory=_offers,
    )

    entrypoint.enter_with_commands(
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
            name="seat_maps",
            callback=_seat_maps,
            settings_class=_SeatMapsSettings,
        ),
    )
