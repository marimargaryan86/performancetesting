import asyncio
import contextlib
import dataclasses
from collections.abc import Iterable, Mapping

import grpc

from snowfall.project.junction.go.service.places.v1 import (
    places_pb2 as locations_pb2,
)
from snowfall.project.junction.go.service.places.v1 import (
    places_pb2_grpc as locations_pb2_grpc,
)
from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.v1 import latlng_pb2


class _PlaceNotFoundError(ValueError):
    """Raised when a place is not found for a given set of coordinates."""


@dataclasses.dataclass(frozen=True)
class Segment:
    origin: models_pb2.Place
    destination: models_pb2.Place


@dataclasses.dataclass(frozen=True)
class Route:
    segments: list[Segment]


class Routes:
    def __init__(
        self,
        planner: planner_pb2_grpc.PlannerServiceStub,
        places: places_pb2_grpc.PlacesServiceStub,
        locations: locations_pb2_grpc.LocationsServiceStub,
        place_search_radius: int,
    ):
        self._planner = planner
        self._places = places
        self._locations = locations
        self._search_radius = place_search_radius

    async def find_routes(
        self,
        origin: models_pb2.Place,
        destination: models_pb2.Place,
    ) -> list[Route]:
        try:
            route_response = await self._planner.FindRoutes(
                planner_pb2.FindRoutesRequest(
                    origins=await self._find_location_coordinates(origin.coordinates),
                    destinations=await self._find_location_coordinates(
                        destination.coordinates,
                    ),
                ),
            )
        except grpc.aio.AioRpcError as err:
            if err.code() == grpc.StatusCode.INVALID_ARGUMENT:
                return []

            raise

        segments = [
            segment for route in route_response.routes for segment in route.segments
        ]
        resolved_places = await self._resolve_coordinates(
            [
                place
                for segment in segments
                for place in (segment.origin, segment.destination)
            ],
        )
        resolved_routes = []

        for route in route_response.routes:
            with contextlib.suppress(KeyError):
                resolved_routes.append(self._resolve_route(route, resolved_places))

        return resolved_routes

    async def _find_location_coordinates(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> list[latlng_pb2.LatLng]:
        found_locations = await self._locations.ListNearbyLocations(
            locations_pb2.ListNearbyLocationsRequest(
                coordinates=coordinates,
                precision=locations_pb2.SearchPrecision(
                    mode=locations_pb2.SearchPrecision.MODE_AREA,
                ),
            ),
        )

        return list(
            {
                location.coordinates.SerializeToString(
                    deterministic=True,
                ): location.coordinates
                for location in found_locations.locations
            }.values(),
        )

    def _resolve_route(
        self,
        route: planner_pb2.FindRoutesResponse.Route,
        resolved_places: Mapping[bytes, models_pb2.Place],
    ) -> Route:
        return Route(
            segments=[
                Segment(
                    origin=resolved_places[
                        segment.origin.SerializeToString(deterministic=True)
                    ],
                    destination=resolved_places[
                        segment.destination.SerializeToString(deterministic=True)
                    ],
                )
                for segment in route.segments
            ],
        )

    async def _resolve_coordinates(
        self,
        coordinates: Iterable[latlng_pb2.LatLng],
    ) -> dict[bytes, models_pb2.Place]:
        unique_coordinates = {
            coordinate.SerializeToString(deterministic=True): coordinate
            for coordinate in coordinates
        }

        resolved_tasks = await asyncio.gather(
            *[
                self._resolve_coordinate(coordinate)
                for coordinate in unique_coordinates.values()
            ],
            return_exceptions=True,
        )
        resolved_places = {}

        for resolved_task in resolved_tasks:
            if not isinstance(resolved_task, BaseException):
                resolved_places[resolved_task[0]] = resolved_task[1]

        return resolved_places

    async def _resolve_coordinate(
        self,
        coordinate: latlng_pb2.LatLng,
    ) -> tuple[bytes, models_pb2.Place]:
        try:
            return coordinate.SerializeToString(
                deterministic=True,
            ), await self._places.GetPlaceClosestToCoordinates(
                places_pb2.GetPlaceClosestToCoordinatesRequest(
                    coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                        coordinates=coordinate,
                        radius=self._search_radius,
                    ),
                ),
            )
        except grpc.aio.AioRpcError as err:
            raise _PlaceNotFoundError from err
