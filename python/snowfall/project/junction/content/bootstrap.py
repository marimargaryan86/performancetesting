from __future__ import annotations

import dataclasses
import ipaddress
import uuid
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Generic, NamedTuple, TypeAlias, TypeVar

from snowfall.project.junction.content import meta, trips
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server, service

Application = application.Application
TripSearchImplementation = trips.TripSearchImplementation


class ConfigurationError(Exception):
    """Raised when there is a configuration error."""


class Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class ProviderConfiguration(NamedTuple):
    provider_id: uuid.UUID
    provider_name: str
    trip_search_implementation: TripSearchImplementation | None = None


_Settings = TypeVar("_Settings", bound=Settings)

if TYPE_CHECKING:
    ImplementationFactory: TypeAlias = Callable[
        [Application[_Settings]],
        Awaitable[ProviderConfiguration],
    ]


def _grpc_command(
    implementation_factory: ImplementationFactory[_Settings],
) -> application.Callback[_Settings]:
    async def wrapper(  # noqa: WPS217
        app: Application[_Settings],
    ) -> None:
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            create_grpc_services(await implementation_factory(app)),
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()

    return wrapper


def create_grpc_services(config: ProviderConfiguration) -> list[service.Service]:
    trip_service = None

    if config.trip_search_implementation:
        if not config.trip_search_implementation.is_valid():
            raise ConfigurationError("Trip search has unspecified capabilities.")

        trip_service = trips.TripService(
            implementation=config.trip_search_implementation,
        )

    return [
        meta.MetaService(
            meta.MetaImplementation(
                identifier=config.provider_id,
                name=config.provider_name,
                trip_search_capabilities=trip_service.get_capabilities()
                if trip_service
                else None,
            ),
        ),
        *((trip_service,) if trip_service else ()),
    ]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entrypoint(Generic[_Settings], application.Entrypoint):
    settings_class: type[_Settings]
    implementation_factory: ImplementationFactory[_Settings]

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_command(
            application.Command(
                name="grpc",
                callback=_grpc_command(
                    implementation_factory=self.implementation_factory,
                ),
                settings_class=self.settings_class,
            ),
        )
