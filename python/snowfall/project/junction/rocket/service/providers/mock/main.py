from __future__ import annotations

import contextlib
import datetime

import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    bookings as provider_bookings,
)
from snowfall.project.junction.rocket.provider import (
    meta,
    searches,
    service,
)
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.mock import (
    bookings,
    cache,
    pricing,
)
from snowfall.project.junction.rocket.service.providers.mock import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.mock.constant import PROVIDER_ID
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Mock"
_PROVIDERS_TO_DISABLED_OPERATORS = dict[str, list[str]]
_RESELLERS_TO_PROVIDER_OPERATORS = dict[str, _PROVIDERS_TO_DISABLED_OPERATORS]


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    storage_dsn: service.AnyDsn
    reseller_disabled_operators: _RESELLERS_TO_PROVIDER_OPERATORS = pydantic.Field(
        default_factory=dict,
    )


class _BookingsSettings(service.Settings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    storage_dsn: service.AnyDsn


class _PricingSettings(service.ProviderSettings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(car_rental=True),
        booking_capabilities=meta_pb2.BookingCapabilities(
            supports_cancellation=True,
        ),
    )


async def _search_factory(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> searches.SearchImplementation[provider_searches.CarRentalCriteria]:
    search_result_generator = provider_searches.search_result_generator(
        generator=provider_searches.Generator(
            search_result_cache=cache.SearchResultCache(
                client=redis.Client(redis_conn, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        ),
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.search_criteria_task_generator,
        search_result_cache_key_generator=provider_searches.cache_key,
        search_result_generator=search_result_generator,
    )


async def _pricing(app: service.Application[_PricingSettings]) -> None:
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
        search_result_cache=cache.SearchResultCache(
            client=redis_client,
        ),
        quote_cache=cache.QuoteCache(
            client=redis_client,
        ),
        ttl=app.settings.ttl,
    )

    await quote_task_consumer.consume()


async def _bookings(app: service.Application[_BookingsSettings]) -> None:
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
            quote_cache=cache.QuoteCache(
                client=redis_client,
            ),
            booking_storage=storage,
            provider_id=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ),
    ).consume()


async def _bookings_factory(
    app: service.Application[_Settings],
) -> provider_bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    raw_to_booking = bookings.Transformer().raw_to_booking

    return provider_bookings.Implementation(
        storage=storage,
        transformer=raw_to_booking,
        cancellation_handler=bookings.CancellationHandler(
            booking_storage=storage,
            transformer=raw_to_booking,
        ).cancel,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="mock",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
        bookings_factory=_bookings_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_pricing,
            settings_class=_PricingSettings,
        ),
        service.Command(
            name="bookings",
            callback=_bookings,
            settings_class=_BookingsSettings,
        ),
    )
