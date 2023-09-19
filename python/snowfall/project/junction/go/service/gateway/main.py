from __future__ import annotations

import datetime
import ipaddress
from typing import TypeVar, cast

import pydantic
from aio_pika import robust_connection
from google.protobuf import message

from snowfall.project.junction.go.service.gateway import (
    bookings,
    meta,
    offers,
    providers,
    trips,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer, producer, protocol, types
from snowfall.stdlib.transport.grpc import server as grpc_server


class _SharedSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    providers: dict[str, str] = pydantic.Field(default_factory=dict)
    redis_dsn: pydantic.RedisDsn


class _ConsumeSettings(_SharedSettings):
    search_timeout: datetime.timedelta = datetime.timedelta(seconds=30)
    trip_search_timeout: datetime.timedelta = datetime.timedelta(seconds=10)


class _ServeSettings(_SharedSettings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


_BootstrapReturn = tuple[
    robust_connection.RobustConnection,
    redis.Client[bytes],
    providers.Collection,
]


_SharedSettingsGeneric = TypeVar("_SharedSettingsGeneric", bound=_SharedSettings)


async def _bootstrap(
    app: application.AsyncApplication[_SharedSettingsGeneric],
) -> _BootstrapReturn:
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    redis_client = await redis_factory.make_client(
        app,
        app.settings.redis_dsn,
        decode_responses=False,
    )

    all_providers = await providers.Collection.from_identifier_channel_tuples(
        [
            providers.IdentifierChannelTuple(
                identifier=identifier,
                channel=await grpc_factory.make_insecure_channel(app, dsn),
            )
            for identifier, dsn in app.settings.providers.items()
        ],
    )

    return amqp_connection, redis_client, all_providers


async def _consume(app: application.AsyncApplication[_ConsumeSettings]) -> None:
    amqp_connection, redis_client, all_providers = await _bootstrap(app)

    legacy_offers_queue = offers.Queue(
        name_prefix=app.name,
        providers_list=all_providers,
        repository=offers.Repository(
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange(name=app.name),
            ),
            client=redis_client,
        ),
        timeout=app.settings.search_timeout,
    )

    trips_queue = trips.Queue(
        name_prefix=app.name,
        providers_list=all_providers,
        repository=trips.Repository(
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange(name=app.name),
            ),
            client=redis_client,
        ),
        timeout=app.settings.trip_search_timeout,
    )

    await consumer.QueueConsumer(
        connection=amqp_connection,
        queues=cast(
            list[protocol.Queue[message.Message]],
            [
                legacy_offers_queue,
                trips_queue,
            ],
        ),
    ).consume()


async def _serve(app: application.AsyncApplication[_ServeSettings]) -> None:
    amqp_connection, redis_client, all_providers = await _bootstrap(app)

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
                        connection=amqp_connection,
                        exchange=types.Exchange(name=app.name),
                    ),
                    client=redis_client,
                ),
            ),
            trips.Service(
                repository=trips.Repository(
                    producer=producer.Producer(
                        connection=amqp_connection,
                        exchange=types.Exchange(name=app.name),
                    ),
                    client=redis_client,
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
