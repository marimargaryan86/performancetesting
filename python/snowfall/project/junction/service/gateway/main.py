from __future__ import annotations

import datetime
import ipaddress
from typing import NamedTuple, TypeVar, cast

import pydantic
from aio_pika import abc
from google.protobuf import message

from snowfall.project.junction.go.service.places.v1 import places_pb2_grpc
from snowfall.project.junction.service.gateway import (
    meta,
    providers,
    stops,
)
from snowfall.project.junction.service.gateway.trips import cache as trips_cache
from snowfall.project.junction.service.gateway.trips import (
    request as trips_request,
)
from snowfall.project.junction.service.gateway.trips import server as trips_server
from snowfall.project.junction.service.gateway.trips import task as trips_task
from snowfall.project.junction.service.gateway.v1 import trips_pb2
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
    places_address: str
    stops_resolver_timeout: datetime.timedelta = datetime.timedelta(seconds=5)
    trip_search_cache_ttl: datetime.timedelta = datetime.timedelta(days=1)
    trip_search_timeout: datetime.timedelta = datetime.timedelta(seconds=10)


class _ServeSettings(_SharedSettings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _BootstrapReturn(NamedTuple):
    amqp_connection: abc.AbstractConnection
    redis_client: redis_types.Client[bytes]
    providers: providers.Collection
    trip_search_runner: tasks.Runner[trips_pb2.TripSearchResult]


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

    trip_search_runner = tasks.Runner[trips_pb2.TripSearchResult](
        client=redis_client,
        ttl=_task_ttl,
        gc_probability=_gc_probability,
    )

    return _BootstrapReturn(
        amqp_connection=amqp_connection,
        redis_client=redis_client,
        providers=all_providers,
        trip_search_runner=trip_search_runner,
    )


async def _consume(app: application.Application[_ConsumeSettings]) -> None:
    bootstrap_return = await _bootstrap(app)

    places_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.places_address,
    )

    trips_queue = trips_task.Queue(
        name_prefix=app.name,
        request_generator=trips_request.Generator(
            providers_list=bootstrap_return.providers,
            stop_resolver=stops.Resolver(
                stub=places_pb2_grpc.PlacesServiceStub(channel=places_channel),
                timeout=app.settings.stops_resolver_timeout,
            ).from_ids,
        ),
        runner=bootstrap_return.trip_search_runner,
        searcher=trips_task.Searcher(
            cache_factory=trips_cache.Factory(
                client=bootstrap_return.redis_client,
                ttl=app.settings.trip_search_cache_ttl,
            ),
            timeout=app.settings.trip_search_timeout,
        ),
    )

    await consumer.QueueConsumer(
        connection=bootstrap_return.amqp_connection,
        queues=cast(
            list[protocol.Queue[message.Message]],
            [
                trips_queue,
            ],
        ),
    ).consume()


async def _serve(app: application.Application[_ServeSettings]) -> None:
    bootstrap_return = await _bootstrap(app)

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            meta.Service(
                providers_collection=bootstrap_return.providers,
            ),
            trips_server.Service(
                producer=producer.Producer(
                    connection=bootstrap_return.amqp_connection,
                    exchange=types.Exchange(name=app.name),
                ),
                runner=bootstrap_return.trip_search_runner,
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
