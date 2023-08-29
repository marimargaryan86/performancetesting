from __future__ import annotations

import datetime
import ipaddress

import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.gateway import (
    bookings,
    meta,
    offers,
    providers,
)
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server as grpc_server


class _ConsumeSettings(application.Settings):
    amqp_dsn: pydantic.AnyUrl
    providers: dict[str, str] = pydantic.Field(default_factory=dict)
    redis_dsn: pydantic.AnyUrl
    search_timeout: datetime.timedelta = datetime.timedelta(seconds=30)


class _ServeSettings(application.Settings):
    amqp_dsn: pydantic.AnyUrl
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    providers: dict[str, str] = pydantic.Field(default_factory=dict)
    redis_dsn: pydantic.AnyUrl


async def _consume(app: application.AsyncApplication[_ConsumeSettings]) -> None:
    connection = await app.stack.enter_async_context(
        types.Connection(str(app.settings.amqp_dsn)),
    )
    redis_conn = await app.stack.enter_async_context(
        aioredis.from_url(
            str(app.settings.redis_dsn),
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    all_providers = await providers.Collection.from_identifier_address_tuples(
        [
            providers.IdentifierAddressTuple(*provider_tuple)
            for provider_tuple in app.settings.providers.items()
        ],
    )

    offers_consumer = offers.Consumer(
        providers_list=all_providers,
        repository=offers.Repository(
            producer=producer.Producer(
                connection=connection,
                exchange=types.Exchange(name=app.name),
            ),
            client=redis.Client(redis_conn),
        ),
        timeout=app.settings.search_timeout,
    )
    amqp_consumer = consumer.Consumer[amqp_pb2.TripOfferSearchTask](
        connection=connection,
        queue_name="{0}_offer_searches".format(app.name),
        binds=[(types.Exchange(app.name), "offers.search.*")],
    )

    await amqp_consumer.consume(offers_consumer.consume)


async def _serve(app: application.AsyncApplication[_ServeSettings]) -> None:
    connection = await app.stack.enter_async_context(
        types.Connection(str(app.settings.amqp_dsn)),
    )
    redis_conn = await app.stack.enter_async_context(
        aioredis.from_url(
            str(app.settings.redis_dsn),
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    all_providers = await providers.Collection.from_identifier_address_tuples(
        [
            providers.IdentifierAddressTuple(*provider_tuple)
            for provider_tuple in app.settings.providers.items()
        ],
    )

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            bookings.Service(
                providers_collection=all_providers,
            ),
            meta.Service(
                providers_collection=all_providers,
            ),
            offers.Service(
                repository=offers.Repository(
                    producer=producer.Producer(
                        connection=connection,
                        exchange=types.Exchange(name=app.name),
                    ),
                    client=redis.Client(redis_conn),
                ),
            ),
        ],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="gateway")

    entrypoint.enter_with_commands(
        application.Command(
            name="consume",
            callback=_consume,
            settings_class=_ConsumeSettings,
        ),
        application.Command(
            name="serve",
            callback=_serve,
            settings_class=_ServeSettings,
        ),
    )
