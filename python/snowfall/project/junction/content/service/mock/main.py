from __future__ import annotations

import uuid
from typing import Any, cast

from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.content.service.mock import (
    client,
    trips,
)
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.persistence import filesystem

_PROVIDER_ID = uuid.UUID("f9ce75d1-2025-4ab5-b5d7-69e4c14c053e")
_PROVIDER_NAME = "Mock"


async def _factory(
    app: bootstrap.Application[bootstrap.Settings],
) -> bootstrap.ProviderConfiguration:
    stop_repository = client.StopRepository(
        stops=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(__name__).load("stops.json"),
        ),
    )
    route_repository = client.RouteRepository(
        stop_repository=stop_repository,
        routes=cast(
            list[list[str]],
            filesystem.PkgLoader(__name__).load("routes.json"),
        ),
    )
    trip_searcher = trips.Trips(
        search_client=client.MockClient(
            route_repository=route_repository,
        ),
        transformer=trips.Transformer(),
    )

    return bootstrap.ProviderConfiguration(
        provider_id=_PROVIDER_ID,
        provider_name=_PROVIDER_NAME,
        trip_search_implementation=bootstrap.TripSearchImplementation(
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            one_way=trip_searcher.find_one_way,
            round_trip=trip_searcher.find_round_trip,
            multi_city=trip_searcher.find_multi_city,
        ),
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="junction-content-mock",
        implementation_factory=_factory,
        settings_class=bootstrap.Settings,
    )
    entrypoint.enter()
