from __future__ import annotations

import contextlib
import dataclasses
import ipaddress
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Generic, TypeVar

import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import (
    bookings,
    meta,
    searches,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service

# Re-export some service types
AnyDsn = application.AnyDsn
Application = application.Application
Command = application.Command
Settings = application.Settings


class ProviderSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    redis_dsn: pydantic.RedisDsn


_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
_Settings = TypeVar("_Settings", bound=ProviderSettings)

if TYPE_CHECKING:
    MetaFactory = Callable[[], Awaitable[meta.MetaImplementation]]
    SearchFactory = Callable[
        [
            application.Application[_Settings],
            abc.AbstractConnection,
            aioredis.Redis[bytes],  # TODO(jyggen): accept Redis client instead.
            contextlib.AsyncExitStack,
        ],
        Awaitable[searches.SearchImplementation[_SearchCriteria]],
    ]
    SF = SearchFactory[_Settings, _SearchCriteria]
    BookingFactory = Callable[
        [application.Application[_Settings]],
        Awaitable[bookings.Implementation],
    ]


def _grpc_command(  # noqa: WPS217
    meta_factory: MetaFactory,
    search_factory: SF[_Settings, _SearchCriteria],
    bookings_factory: BookingFactory[_Settings] | None = None,
) -> application.Callback[_Settings]:
    async def wrapper(  # noqa: WPS217
        app: application.Application[_Settings],
    ) -> None:
        meta_implementation = await meta_factory()
        services: list[grpc_service.Service] = [
            meta.MetaService(
                provider_id=meta_implementation.identifier,
                provider_name=meta_implementation.name,
                booking_capabilities=meta_implementation.booking_capabilities,
            ),
        ]
        redis_conn = await redis_factory.make_connection(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )
        connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

        search_implementation = await search_factory(
            app,
            connection,
            redis_conn,
            app.stack,
        )

        services.append(
            searches.SearchService(
                searches.Searcher.from_implementation(
                    implementation=search_implementation,
                    redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
                ),
                provider_name=meta_implementation.name,
            ),
        )

        if bookings_factory:
            bookings_implementation = await bookings_factory(app)
            services.append(
                bookings.BookingService(implementation=bookings_implementation),
            )

        server = grpc_server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            services,
        )

        async with server.serve() as running:
            await running.wait_for_termination()

    return wrapper


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entrypoint(
    Generic[_Settings, _SearchCriteria],
    application.Entrypoint,
):
    settings_class: type[_Settings]
    meta_factory: MetaFactory
    search_factory: SearchFactory[_Settings, _SearchCriteria]
    bookings_factory: BookingFactory[_Settings] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_command(
            application.Command(
                name="grpc",
                callback=_grpc_command(
                    self.meta_factory,
                    self.search_factory,
                    self.bookings_factory,
                ),
                settings_class=self.settings_class,
            ),
        )
