from __future__ import annotations

import ipaddress
import uuid
from typing import Any, cast

from snowfall.project.junction.content import meta
from snowfall.project.junction.content import trips as provider_trips
from snowfall.project.junction.content.service.mock import (
    client,
    trips,
)
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server

_PROVIDER_ID = uuid.UUID("f9ce75d1-2025-4ab5-b5d7-69e4c14c053e")
_PROVIDER_NAME = "Mock"


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


async def _serve(app: application.Application[_Settings]) -> None:
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

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            meta.MetaService(
                meta.MetaImplementation(
                    identifier=_PROVIDER_ID,
                    name=_PROVIDER_NAME,
                    trip_search_capabilities=meta_pb2.TripSearchCapabilities(
                        is_supported=True,
                        supports_round_trip=True,
                        supports_multi_city=True,
                        stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                        supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
                        passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    ),
                ),
            ),
            provider_trips.TripService(
                one_way=trip_searcher.find_one_way,
                round_trip=trip_searcher.find_round_trip,
                multi_city=trip_searcher.find_multi_city,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="mock")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_Settings,
        ),
    )
