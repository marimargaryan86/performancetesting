from __future__ import annotations

import contextlib
import dataclasses
import ipaddress
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Generic, TypeVar

import pydantic
from aio_pika import abc
from google.protobuf import message
from redis import asyncio as aioredis

from snowfall.project.junction.provider import (
    bookings,
    meta,
    offers,
    simple_offers,
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
    provider_company_id: str
    redis_dsn: pydantic.RedisDsn
    reseller_providers: dict[str, list[str]]


class PriceQuoteSettings(application.Settings):
    provider_company_id: str


_SearchCriteriaTask = TypeVar("_SearchCriteriaTask", bound=message.Message)
_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
_Settings = TypeVar("_Settings", bound=ProviderSettings)

if TYPE_CHECKING:
    MetaFactory = Callable[[], Awaitable[meta.MetaImplementation]]
    OffersFactory = Callable[
        [
            application.Application[_Settings],
            abc.AbstractConnection,
            aioredis.Redis[bytes],  # TODO: accept Redis client instead.
            contextlib.AsyncExitStack,
        ],
        Awaitable[
            offers.OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria]
        ],
    ]
    SimpleOffersFactory = Callable[
        [
            application.Application[_Settings],
            abc.AbstractConnection,
            aioredis.Redis[bytes],  # TODO: accept Redis client instead.
            contextlib.AsyncExitStack,
        ],
        Awaitable[simple_offers.SimpleOfferSearchImplementation[_SearchCriteria,]],
    ]
    OF = OffersFactory[_Settings, _SearchCriteriaTask, _SearchCriteria]
    SF = SimpleOffersFactory[_Settings, _SearchCriteria]
    BookingFactory = Callable[
        [application.Application[_Settings]],
        Awaitable[bookings.Implementation],
    ]


def _grpc_command(  # noqa: WPS217
    meta_factory: MetaFactory,
    offers_factory: OF[_Settings, _SearchCriteriaTask, _SearchCriteria] | None = None,
    simple_offers_factory: SF[_Settings, _SearchCriteria] | None = None,
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
                        if str(meta_implementation.identifier) in providers
                    ],
                    provider_company_id=app.settings.provider_company_id,
                    provider_name=meta_implementation.name,
                ),
            )

        if simple_offers_factory:
            simple_offers_implementation = await simple_offers_factory(
                app,
                connection,
                redis_conn,
                app.stack,
            )
            services.append(
                simple_offers.SimpleSearchService(
                    simple_offers.SimpleOfferSearcher.from_implementation(
                        implementation=simple_offers_implementation,
                        redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
                    ),
                    enabled_resellers=[
                        reseller_id
                        for reseller_id, providers in app.settings.reseller_providers.items()
                        if str(meta_implementation.identifier) in providers
                    ],
                    provider_company_id=app.settings.provider_company_id,
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


def _offers_command(
    meta_factory: MetaFactory,
    offers_factory: OffersFactory[_Settings, _SearchCriteriaTask, _SearchCriteria],
) -> application.Callback[_Settings]:
    async def wrapper(app: application.Application[_Settings]) -> None:
        meta_implementation = await meta_factory()
        redis_conn = await redis_factory.make_connection(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )
        connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

        trip_search_consumer = offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
            implementation=await offers_factory(app, connection, redis_conn, app.stack),
            app_name=app.name,
            pay_company_id=app.settings.provider_company_id,
            provider_name=meta_implementation.name,
            provider_id=str(meta_implementation.identifier),
            reseller_providers=app.settings.reseller_providers,
        )

        await trip_search_consumer.consume()

    return wrapper


def _simple_offers_command(
    meta_factory: MetaFactory,
    simple_offers_factory: SimpleOffersFactory[_Settings, _SearchCriteria],
) -> application.Callback[_Settings]:
    async def wrapper(app: application.Application[_Settings]) -> None:
        meta_implementation = await meta_factory()
        redis_conn = await redis_factory.make_connection(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )
        connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

        trip_search_consumer = simple_offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
            implementation=await simple_offers_factory(
                app,
                connection,
                redis_conn,
                app.stack,
            ),
            app_name=app.name,
            pay_company_id=app.settings.provider_company_id,
            provider_name=meta_implementation.name,
            provider_id=str(meta_implementation.identifier),
            reseller_providers=app.settings.reseller_providers,
        )

        await trip_search_consumer.consume()

    return wrapper


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entrypoint(
    Generic[_Settings, _SearchCriteriaTask, _SearchCriteria],
    application.Entrypoint,
):
    settings_class: type[_Settings]
    meta_factory: MetaFactory
    offers_factory: (
        OffersFactory[
            _Settings,
            _SearchCriteriaTask,
            _SearchCriteria,
        ]
        | None
    ) = None
    simple_offers_factory: SimpleOffersFactory[_Settings, _SearchCriteria] | None = None
    bookings_factory: BookingFactory[_Settings] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_command(
            application.Command(
                name="grpc",
                callback=_grpc_command(
                    self.meta_factory,
                    self.offers_factory,
                    self.simple_offers_factory,
                    self.bookings_factory,
                ),
                settings_class=self.settings_class,
            ),
        )

        # backwards compatibility
        if self.offers_factory:
            self.add_command(
                application.Command(
                    name="offers",
                    callback=_offers_command(self.meta_factory, self.offers_factory),
                    settings_class=self.settings_class,
                ),
            )

        # backwards compatibility
        if self.simple_offers_factory:
            self.add_command(
                application.Command(
                    name="simple-offers",
                    callback=_simple_offers_command(
                        self.meta_factory,
                        self.simple_offers_factory,
                    ),
                    settings_class=self.settings_class,
                ),
            )
