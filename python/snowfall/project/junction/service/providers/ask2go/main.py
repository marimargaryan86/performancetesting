from __future__ import annotations

import contextlib
import datetime
import random
from typing import Any, Sequence, cast

import aiosmtplib
import httpx
import pydantic
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    airports,
    cabin_classes,
    notifications,
    offers,
    repository,
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
from snowfall.stdlib import h3, service
from snowfall.stdlib.instrumentation import httpx_metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import search as search_models

_OFFERS = "offers"


class _OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl


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


class _SearchSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _SeatMapsSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    amqp_dsn: pydantic.AnyUrl
    http_timeout: float = 60.0


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_conn: aioredis.Redis[str] = await stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
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
                h3_mapping=h3.H3MappingRepository[airports.Airport](
                    mapping=airports.AirportRepository(
                        airports_data=cast(
                            list[dict[str, Any]],
                            filesystem.PkgLoader(
                                "snowfall.project.junction.service.providers.ask2go.main",
                            ).load("airports.json"),
                        ),
                    ).all_(),
                    resolution=7,
                ),
            ).from_search_task,
            internal_exchange_name=app.name,
        )

        await trip_search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    http2=True,
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
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


async def _searches(app: service.Application[_SearchSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    http2=True,
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        ask2go_client = client.Ask2GoClient(
            api_base_url=app.settings.api_base_url,
            api_booking_base_url=app.settings.api_booking_base_url,
            http_client=http_client,
        )
        search_adapter = search.Adapter(
            ask2go_client=ask2go_client,
            poll_retries_limit=app.settings.poll_retries_limit,
            wait_time_between_polling=app.settings.wait_time_between_polling,
        )
        await offers.SearchCriteriaConsumer[
            amqp_pb2.SearchCriteriaTask,
            search_models.CreateSearchCriteria,
        ](
            search_criteria_generator_func=search_adapter.search_criteria_generator,
            consumer=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("ask2go"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("ask2go"),
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
                offer_group_cache_key_func=search_adapter.generate_cache_key,
                offer_group_generator=a2g_offers.offer_group_generator(
                    a2g_adapter=search_adapter,
                    a2g_transformer=transformer.OfferTransformer(
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
                            client=redis.Client[bytes](
                                redis_connection,
                                prefix=app.name,
                            ),
                        ),
                        price_cache=cache.PriceQuoteCache(
                            client=redis.Client[bytes](
                                redis_connection,
                                prefix=app.name,
                            ),
                        ),
                        offer_ttl=app.settings.ttl,
                    ),
                ),
            ),
        ).consume()


async def _price_quotes(app: service.Application[_SearchSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    http2=True,
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
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
        ).consume()


async def _seat_maps(app: service.Application[_SeatMapsSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    http2=True,
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
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
    entrypoint = service.Entrypoint(name="ask2go")

    entrypoint.enter_with_commands(
        service.Command(
            name=_OFFERS,
            callback=_offers,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
        service.Command(
            name="searches",
            callback=_searches,
            settings_class=_SearchSettings,
        ),
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_SearchSettings,
        ),
        service.Command(
            name="seat_maps",
            callback=_seat_maps,
            settings_class=_SeatMapsSettings,
        ),
    )
