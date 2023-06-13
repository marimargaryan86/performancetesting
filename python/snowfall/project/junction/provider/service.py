from __future__ import annotations

import contextlib
import dataclasses
import ipaddress
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Generic, TypeVar

import pydantic
from google.protobuf import message
from redis import asyncio as aioredis

from snowfall.project.junction.provider import bookings, meta, offers
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.grpc import server as grpc_server

# Re-export some service types
AnyDsn = service.AnyDsn
Application = service.Application
AsyncApplication = service.AsyncApplication
Command = service.Command
Settings = service.Settings


class ProviderSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    provider_company_id: str
    redis_dsn: pydantic.AnyUrl
    reseller_providers: dict[str, list[str]]


class PriceQuoteSettings(service.Settings):
    provider_company_id: str


_SearchCriteriaTask = TypeVar("_SearchCriteriaTask", bound=message.Message)
_SearchCriteria = TypeVar("_SearchCriteria", bound=object)

_Settings = TypeVar("_Settings", bound=ProviderSettings)

if TYPE_CHECKING:
    MetaFactory = Callable[[], Awaitable[meta.MetaImplementation]]
    OffersFactory = Callable[
        [
            service.Application[_Settings],
            types.Connection,
            aioredis.Redis[bytes],
            contextlib.AsyncExitStack,
        ],
        Awaitable[
            offers.OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria]
        ],
    ]

    OptionalOF = (
        OffersFactory[_Settings, _SearchCriteriaTask, _SearchCriteria]  # noqa: WPS465
        | None
    )
    BookingFactory = Callable[
        [service.AsyncApplication[_Settings]],
        Awaitable[bookings.Implementation],
    ]


def _grpc_command(  # noqa: WPS210, WPS217
    meta_factory: MetaFactory,
    offers_factory: OptionalOF[_Settings, _SearchCriteriaTask, _SearchCriteria] = None,
    bookings_factory: BookingFactory[_Settings] | None = None,
) -> service.Callback[_Settings]:
    async def wrapper(  # noqa: WPS210, WPS217
        app: service.AsyncApplication[_Settings],
    ) -> None:
        meta_implementation = await meta_factory()
        services: list[grpc_server.Service] = [
            meta.MetaService(
                provider_id=meta_implementation.identifier,
                provider_name=meta_implementation.name,
            ),
        ]
        redis_conn: aioredis.Redis[bytes] = await app.stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=False,
            ).client(),
        )
        connection = await app.stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        if offers_factory:
            offers_implementation = await offers_factory(
                app,
                connection,
                redis_conn,
                app.stack,
            )
            services.append(
                offers.OfferSearchService(
                    offers.TripOfferSearcher.from_implementation(
                        implementation=offers_implementation,
                        redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
                    ),
                    enabled_resellers=[
                        reseller_id
                        for reseller_id, providers in app.settings.reseller_providers.items()
                        if meta_implementation.name in providers
                        or meta_implementation.name.lower() in providers
                    ],
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


def _offers_command(
    factory: OffersFactory[_Settings, _SearchCriteriaTask, _SearchCriteria],
) -> service.Callback[_Settings]:
    async def wrapper(app: service.AsyncApplication[_Settings]) -> None:
        redis_conn: aioredis.Redis[bytes] = await app.stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=False,
            ).client(),
        )
        connection = await app.stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        trip_search_consumer = offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
            implementation=await factory(app, connection, redis_conn, app.stack),
            app_name=app.name,
            pay_company_id=app.settings.provider_company_id,
            provider_name=app.name,
            reseller_providers=app.settings.reseller_providers,
        )

        await trip_search_consumer.consume()

    return wrapper


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entrypoint(
    Generic[_Settings, _SearchCriteriaTask, _SearchCriteria],
    service.Entrypoint,
):
    settings_class: type[_Settings]
    meta_factory: MetaFactory
    offers_factory: OffersFactory[
        _Settings,
        _SearchCriteriaTask,
        _SearchCriteria,
    ] | None = None
    bookings_factory: BookingFactory[_Settings] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_command(
            service.Command(
                name="grpc",
                callback=_grpc_command(
                    self.meta_factory,
                    self.offers_factory,
                    self.bookings_factory,
                ),
                settings_class=self.settings_class,
            ),
        )

        # backwards compatibility
        if self.offers_factory:
            self.add_command(
                service.Command(
                    name="offers",
                    callback=_offers_command(self.offers_factory),
                    settings_class=self.settings_class,
                ),
            )
