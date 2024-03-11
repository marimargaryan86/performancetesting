from __future__ import annotations

import datetime
import ipaddress
from typing import NamedTuple, TypeVar, cast

import pydantic
from aio_pika import abc
from google.protobuf import message

from snowfall.project.junction.rocket.service.gateway import (
    bookings,
    meta,
    providers,
    searches,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import amqp_pb2
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    redis_factory,
    tasks,
)
from snowfall.stdlib.transport.amqp import consumer, producer, protocol, types
from snowfall.stdlib.transport.grpc import server as grpc_server


class _SharedSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    providers: dict[str, str] = pydantic.Field(default_factory=dict)
    redis_dsn: pydantic.RedisDsn


class _ConsumeSettings(_SharedSettings):
    search_timeout: datetime.timedelta = datetime.timedelta(seconds=30)


class _ServeSettings(_SharedSettings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _BootstrapReturn(NamedTuple):
    amqp_connection: abc.AbstractConnection
    redis_client: redis_types.Client[bytes]
    providers: providers.Collection
    search_task_result_runner: tasks.Runner[amqp_pb2.SearchTaskResult]


_SharedSettingsGeneric = TypeVar("_SharedSettingsGeneric", bound=_SharedSettings)
_task_ttl = datetime.timedelta(minutes=5)
_gc_probability = 0.01


async def _bootstrap(
    app: application.Application[_SharedSettingsGeneric],
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

    search_task_result_runner = tasks.Runner[amqp_pb2.SearchTaskResult](
        client=redis_client,
        ttl=_task_ttl,
        gc_probability=_gc_probability,
    )

    return _BootstrapReturn(
        amqp_connection=amqp_connection,
        redis_client=redis_client,
        providers=all_providers,
        search_task_result_runner=search_task_result_runner,
    )


async def _consume(app: application.Application[_ConsumeSettings]) -> None:
    bootstrap_return = await _bootstrap(app)
    searches_queue = searches.Queue(
        name_prefix=app.name,
        providers_list=bootstrap_return.providers,
        runner=bootstrap_return.search_task_result_runner,
        timeout=app.settings.search_timeout,
    )

    await consumer.QueueConsumer(
        connection=bootstrap_return.amqp_connection,
        queues=cast(
            list[protocol.Queue[message.Message]],
            [
                searches_queue,
            ],
        ),
    ).consume()


async def _serve(app: application.Application[_ServeSettings]) -> None:
    bootstrap_return = await _bootstrap(app)

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            bookings.Service(
                providers_collection=bootstrap_return.providers,
            ),
            meta.Service(
                providers_collection=bootstrap_return.providers,
            ),
            searches.Service(
                producer=producer.Producer(
                    connection=bootstrap_return.amqp_connection,
                    exchange=types.Exchange(name=app.name),
                ),
                runner=bootstrap_return.search_task_result_runner,
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
