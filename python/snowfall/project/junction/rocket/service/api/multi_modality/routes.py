from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import datetime
import types
from collections.abc import Iterable, Mapping
from typing import Self

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
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.v1 import latlng_pb2

_MCT_FLIGHT_PREFIX_MINUTES = 75
_MCT_FLIGHT_SUFFIX_MINUTES = 45
_MCT_TRAIN_PREFIX_MINUTES = 30
_MCT_TRAIN_SUFFIX_MINUTES = 15
_MCT_MAPPING = types.MappingProxyType({
    segment_type_pb2.SEGMENT_TYPE_FLIGHT: (
        datetime.timedelta(minutes=_MCT_FLIGHT_PREFIX_MINUTES),
        datetime.timedelta(minutes=_MCT_FLIGHT_SUFFIX_MINUTES),
    ),
    segment_type_pb2.SEGMENT_TYPE_TRAIN: (
        datetime.timedelta(minutes=_MCT_TRAIN_PREFIX_MINUTES),
        datetime.timedelta(minutes=_MCT_TRAIN_SUFFIX_MINUTES),
    ),
})


class _PlaceNotFoundError(ValueError):
    """Raised when a place is not found for a given set of coordinates."""


@dataclasses.dataclass(frozen=True)
class Segment:
    origin: models_pb2.Place
    destination: models_pb2.Place
    type: segment_type_pb2.SegmentType.ValueType
    mct_prefix: datetime.timedelta
    mct_suffix: datetime.timedelta

    @classmethod
    def create(
        cls,
        origin: models_pb2.Place,
        destination: models_pb2.Place,
        segment_type: segment_type_pb2.SegmentType.ValueType,
    ) -> Self:
        mct = _MCT_MAPPING[segment_type]
        return cls(
            origin=origin,
            destination=destination,
            type=segment_type,
            mct_prefix=mct[0],
            mct_suffix=mct[1],
        )


@dataclasses.dataclass(frozen=True)
class Route:
    segments: list[Segment]

    def reduce(self) -> Route:
        if not self.segments:
            return Route(segments=[])

        new_segments = []
        current_segment: Segment = self.segments[0]

        for segment in self.segments[1:]:
            if segment.type == current_segment.type:
                current_segment = Segment.create(
                    origin=current_segment.origin,
                    destination=segment.destination,
                    segment_type=current_segment.type,
                )
            else:
                new_segments.append(current_segment)
                current_segment = segment

        new_segments.append(current_segment)
        return Route(segments=new_segments)


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
                    origins=await self._find_location_coordinates(origin),
                    destinations=await self._find_location_coordinates(destination),
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
                resolved_routes.append(
                    self._resolve_route(route, resolved_places).reduce(),
                )

        return resolved_routes

    async def _find_location_coordinates(
        self,
        place: models_pb2.Place,
    ) -> list[latlng_pb2.LatLng]:
        found_locations = await self._locations.ListNearbyLocations(
            locations_pb2.ListNearbyLocationsRequest(
                coordinates=place.coordinates,
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
                Segment.create(
                    origin=resolved_places[
                        segment.origin.SerializeToString(deterministic=True)
                    ],
                    destination=resolved_places[
                        segment.destination.SerializeToString(deterministic=True)
                    ],
                    segment_type=segment.segment_type,
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
            response = await self._places.GetPlaceClosestToCoordinates(
                places_pb2.GetPlaceClosestToCoordinatesRequest(
                    coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                        coordinates=coordinate,
                        radius=self._search_radius,
                    ),
                ),
            )
        except grpc.aio.AioRpcError as err:
            raise _PlaceNotFoundError from err

        return coordinate.SerializeToString(deterministic=True), response.place
