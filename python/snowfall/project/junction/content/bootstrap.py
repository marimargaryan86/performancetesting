import uuid
from typing import NamedTuple

from snowfall.project.junction.content import meta, trips
from snowfall.stdlib.transport.grpc import service

TripSearchImplementation = trips.TripSearchImplementation


class ConfigurationError(Exception):
    """Raised when there is a configuration error."""


class ProviderConfiguration(NamedTuple):
    provider_id: uuid.UUID
    provider_name: str
    trip_search_implementation: TripSearchImplementation | None = None


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
