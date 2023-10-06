from __future__ import annotations

import contextlib
import datetime
from typing import Any, cast

import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.provider import bookings as provider_bookings
from snowfall.project.junction.provider import meta, service
from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.provider import trips as provider_trips
from snowfall.project.junction.service.providers.mock import (
    bookings,
    cache,
    client,
    offers,
    pricing,
    trips,
)
from snowfall.project.junction.service.providers.mock.constant import PROVIDER_ID
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Mock"


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    storage_dsn: service.AnyDsn
    realistic_results: bool = False


class _PriceQuotesSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl
    provider_company_id: str
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _BookingsSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl
    storage_dsn: service.AnyDsn


async def _price_quotes(app: service.Application[_PriceQuotesSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            str(app.settings.redis_dsn),
            decode_responses=False,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(str(app.settings.amqp_dsn)),
    )

    await pricing.Consumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("prices"),
        ),
        quoter=pricing.Quoter(
            option_cache=cache.OptionCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            price_quote_cache=cache.PriceQuoteCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        ),
        provider_company_id=app.settings.provider_company_id,
    ).consume()


async def _bookings(app: service.Application[_BookingsSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            str(app.settings.redis_dsn),
            decode_responses=False,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(str(app.settings.amqp_dsn)),
    )
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    await bookings.Consumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booker=bookings.Booker(
            price_quote_cache=cache.PriceQuoteCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            booking_storage=storage,
            provider_id=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ),
    ).consume()


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=PROVIDER_ID, name=_PROVIDER_NAME)


async def _offers_factory(
    app: service.Application[_Settings],
    amqp_conn: types.Connection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> provider_offers.OfferSearchImplementation[offers.Criteria, offers.Criteria]:
    return provider_offers.OfferSearchImplementation(
        search_criteria_task_generator=offers.criteria_task_generator,
        search_criteria_generator=offers.criteria_generator,
        offer_group_cache_key_generator=offers.cache_key,
        offer_group_generator=offers.offer_group_generator(
            generator=offers.Generator(
                realistic_results=app.settings.realistic_results,
                option_cache=cache.OptionCache(
                    client=redis.Client(redis_conn, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ),
        ),
    )


async def _bookings_factory(
    app: service.Application[_Settings],
) -> provider_bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    return provider_bookings.Implementation(
        storage=storage,
        transformer=bookings.Transformer().raw_to_booking,
    )


async def _trips_factory(
    app: service.Application[_Settings],
) -> provider_trips.Implementation:
    stop_repository = client.StopRepository(
        stops=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(__name__).load("stops.json"),
        ),
    )
    route_repository = client.RouteRepository(
        stop_repository=stop_repository,
        routes=cast(
            list[list[str]],
            filesystem.PkgLoader(__name__).load("routes.json"),
        ),
    )
    return trips.Trips(
        search_client=client.MockClient(
            route_repository=route_repository,
        ),
        transformer=trips.Transformer(),
    ).find


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="mock",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        offers_factory=_offers_factory,
        bookings_factory=_bookings_factory,
        trips_factory=_trips_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_PriceQuotesSettings,
        ),
        service.Command(
            name="orders",
            callback=_bookings,
            settings_class=_BookingsSettings,
        ),
    )
