from __future__ import annotations

import datetime

import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    bookings as provider_bookings,
)
from snowfall.project.junction.rocket.provider import meta, searches, service
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.carnect import (
    bookings,
    cache,
    criteria,
    pricing,
)
from snowfall.project.junction.rocket.service.providers.carnect import (
    searches as search_result_generator,
)
from snowfall.project.junction.rocket.service.providers.carnect.constants import (
    PROVIDER_ID,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, httpx_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings

_PROVIDER_NAME = "Carnect"

_DEFAULT_TTL_IN_MINUTES = 15
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class _Settings(service.ProviderSettings):
    api_base_url: pydantic.AnyUrl
    api_username: str
    api_password: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    env_name: str = "local"

    @property
    def is_test(self) -> bool:
        return self.env_name.lower() != "production"

    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    storage_dsn: service.AnyDsn
    # TODO(reuben.t): add disabled operator logic, once operator is available in  model


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(car_rental=True),
        booking_capabilities=meta_pb2.BookingCapabilities(supports_cancellation=True),
    )


async def _search_factory(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
) -> searches.SearchImplementation[criteria.Criteria]:
    carnect_config = carnect_settings.Config(
        timeout=app.settings.api_timeout.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=await httpx_factory.make_client(
            app,
            timeout=app.settings.api_timeout,
        ),
        config=carnect_config,
    )

    result_generator = search_result_generator.SearchResultGenerator(
        carnect_client=carnect_client,
        carnect_config=carnect_config,
        search_result_cache=cache.SearchResultCache(
            client=redis.Client(redis_conn, prefix=app.name),
        ),
        ttl=app.settings.ttl,
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=criteria.search_criteria_generator,
        search_result_cache_key_generator=cache.generate_cache_key,
        search_result_generator=result_generator.gather_search_results,
    )


async def _pricing(
    app: service.Application[_Settings],
) -> None:
    carnect_config = carnect_settings.Config(
        timeout=app.settings.api_timeout.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=await httpx_factory.make_client(
            app,
            timeout=app.settings.api_timeout,
        ),
        config=carnect_config,
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
        search_result_cache=cache.SearchResultCache(client=redis_client),
        quote_cache=cache.QuoteCache(client=redis_client),
        carnect_client=carnect_client,
        carnect_config=carnect_config,
        ttl=app.settings.ttl,
    )

    await quote_task_consumer.consume()


async def _bookings(app: service.Application[_Settings]) -> None:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)

    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    carnect_config = carnect_settings.Config(
        timeout=app.settings.api_timeout.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=http_client,
        config=carnect_config,
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
            carnect_client=carnect_client,
            carnect_config=carnect_config,
            provider_id=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ),
    ).consume()


async def _bookings_factory(
    app: service.Application[_Settings],
) -> provider_bookings.Implementation:
    carnect_config = carnect_settings.Config(
        timeout=app.settings.api_timeout.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=await httpx_factory.make_client(
            app,
            timeout=app.settings.api_timeout,
        ),
        config=carnect_config,
    )

    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    transformer = bookings.Transformer()

    return provider_bookings.Implementation(
        storage=storage,
        transformer=transformer.raw_to_booking,
        cancellation_handler=bookings.CancellationHandler(
            carnect_client=carnect_client,
            carnect_config=carnect_config,
        ).cancel,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="junction-rocket-providers-carnect",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
        bookings_factory=_bookings_factory,
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
