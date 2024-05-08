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
    models_pb2 as locations_models_pb2,
)
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
from snowfall.stdlib.format import protobuf
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

_LOCATION = tuple[latlng_pb2.LatLng, segment_type_pb2.SegmentType.ValueType]


class _PlaceNotFoundError(ValueError):
    """Raised when a place is not found for a given set of coordinates."""


@dataclasses.dataclass(frozen=True)
class Segment:
    origin: models_pb2.Place
    destination: models_pb2.Place
    type: segment_type_pb2.SegmentType.ValueType

    estimated_travel_time: datetime.timedelta
    estimated_daily_departures: int
    estimated_departure_times: Iterable[datetime.datetime]

    mct_prefix: datetime.timedelta
    mct_suffix: datetime.timedelta

    def is_inverse_of(self, other: Segment) -> bool:
        return (
            self.origin.id == other.destination.id
            and self.destination.id == other.origin.id
        )

    def to_inverse(self) -> Segment:
        return self.create(
            origin=self.destination,
            destination=self.origin,
            segment_type=self.type,
        )

    @classmethod
    def create(
        cls,
        origin: models_pb2.Place,
        destination: models_pb2.Place,
        segment_type: segment_type_pb2.SegmentType.ValueType,
        estimated_travel_time: datetime.timedelta | None = None,
        estimated_daily_departures: int = 0,
        estimated_departure_times: Iterable[datetime.datetime] | None = None,
    ) -> Self:
        estimated_travel_time = (
            estimated_travel_time
            if estimated_travel_time is not None
            else datetime.timedelta(hours=0)
        )
        estimated_departure_times = (
            estimated_departure_times if estimated_departure_times is not None else []
        )
        mct = _MCT_MAPPING[segment_type]
        return cls(
            origin=origin,
            destination=destination,
            type=segment_type,
            estimated_travel_time=estimated_travel_time,
            estimated_daily_departures=estimated_daily_departures,
            estimated_departure_times=sorted(estimated_departure_times),
            mct_prefix=mct[0],
            mct_suffix=mct[1],
        )


@dataclasses.dataclass(frozen=True)
class Route:
    segments: list[Segment]
    estimated_travel_time: datetime.timedelta
    estimated_daily_departures: int

    def reduce(self) -> Route:
        if not self.segments:
            return Route(
                segments=[],
                estimated_travel_time=self.estimated_travel_time,
                estimated_daily_departures=self.estimated_daily_departures,
            )

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
        return Route(
            segments=new_segments,
            estimated_travel_time=self.estimated_travel_time,
            estimated_daily_departures=self.estimated_daily_departures,
        )

    def is_inverse_of(self, other: Route) -> bool:
        if len(self.segments) != len(other.segments):
            return False

        segment_pairs = zip(
            self.segments,
            other.segments[::-1],
            strict=True,
        )

        return all(
            outbound.is_inverse_of(inbound) for outbound, inbound in segment_pairs
        )

    def to_inverse(self) -> Route:
        return Route(
            segments=[segment.to_inverse() for segment in self.segments[::-1]],
            estimated_travel_time=self.estimated_travel_time,
            estimated_daily_departures=self.estimated_daily_departures,
        )

    # Based on metadata from route and segments, predict the most likely sequence
    # of departures on which each segment can be taken.
    def optimistic_departures(
        self,
        departure_after: datetime.datetime,
    ) -> list[tuple[Segment, datetime.datetime]]:
        optimistic_departures = []

        for idx, segment in enumerate(self.segments):
            if idx > 0:
                departure_after += segment.mct_prefix

            next_departure = departure_after
            for departure_time in segment.estimated_departure_times:
                if departure_time >= departure_after:
                    next_departure = departure_time
                    break

            optimistic_departures.append((segment, next_departure))

            departure_after = (
                next_departure + segment.estimated_travel_time + segment.mct_suffix
            )

        return optimistic_departures


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
                (place, segment.segment_type)
                for segment in segments
                for place in (segment.origin, segment.destination)
            ],
        )
        resolved_routes = []

        for route in route_response.routes:
            with contextlib.suppress(KeyError):
                resolved_routes.append(
                    self._resolve_route(route, resolved_places),
                )
        return resolved_routes

    async def _find_location_coordinates(
        self,
        place: models_pb2.Place,
    ) -> list[latlng_pb2.LatLng]:
        if place.type == models_pb2.Type.TYPE_CITY:
            # If the place is a city, we need to map it to Go Locations for
            # Planner. The Go Locations are aggregated into a city with the
            # same algorithm as the AREA search for the ListNearbyLocations,
            # so this is the most direct way to get a list of locations contained
            # in the city identified by its coordinates.
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

        # In the case when the Place is not a city, we try to map it to the
        # corresponding Place in Planner, using a heuristic.
        return [(await self._find_best_location(place))]

    # Attemps to map a "Rocket" Place to a "Go" Place using some heuristics.
    async def _find_best_location(
        self,
        place: models_pb2.Place,
    ) -> latlng_pb2.LatLng:
        found_locations = await self._locations.ListNearbyLocations(
            locations_pb2.ListNearbyLocationsRequest(
                coordinates=place.coordinates,
                precision=locations_pb2.SearchPrecision(
                    mode=locations_pb2.SearchPrecision.MODE_AREA,
                ),
            ),
        )

        candidate_locations = []
        for location in found_locations.locations:
            if self._same_type(location, place):
                # If the names match, it's good enough and we return it.
                if location.name == place.name:
                    return location.coordinates

                candidate_locations.append(location)

        if not candidate_locations:
            # If no candidate, we fallback on the coordinates of the Rocket
            # Place. This can still work in Planner because Planner will try
            # to map coordinates to an H3 cell and it could choose a Stop nearby.
            return place.coordinates

        # We could do something smarter, such as fuzzy matching of the name, but
        # for now we return the first candidate.
        # We probably should also sort this by distance to the points and keep
        # the closest one. The Places service does not seem to guarantee that
        # these will be returned sorted by distance.
        return candidate_locations[0]

    def _same_type(
        self,
        location: locations_models_pb2.Location,
        place: models_pb2.Place,
    ) -> bool:
        for location_type in location.types:
            match (place.type, location_type):
                case (
                    models_pb2.Type.TYPE_RAILWAY_STATION,
                    locations_models_pb2.Location.Type.TYPE_RAILWAY_STATION,
                ):
                    return True
                case (
                    models_pb2.Type.TYPE_AIRPORT,
                    locations_models_pb2.Location.Type.TYPE_AIRPORT,
                ):
                    return True

        return False

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
                    estimated_travel_time=segment.estimated_travel_time.ToTimedelta(),
                    estimated_daily_departures=segment.estimated_daily_departures,
                    estimated_departure_times=[
                        protobuf.protobuf_to_datetime(ts)
                        for ts in segment.estimated_departure_times
                    ],
                )
                for segment in route.segments
            ],
            estimated_travel_time=route.estimated_travel_time.ToTimedelta(),
            estimated_daily_departures=route.estimated_daily_departures,
        )

    async def _resolve_coordinates(
        self,
        coordinates: Iterable[_LOCATION],
    ) -> dict[bytes, models_pb2.Place]:
        unique_coordinates = {
            coordinate[0].SerializeToString(deterministic=True): coordinate
            for coordinate in coordinates
        }

        resolved_tasks = await asyncio.gather(
            *[
                self._resolve_coordinate(coordinate[0], coordinate[1])
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
        segment_type: segment_type_pb2.SegmentType.ValueType,
    ) -> tuple[bytes, models_pb2.Place]:
        try:
            response = await self._places.GetPlaceClosestToCoordinates(
                places_pb2.GetPlaceClosestToCoordinatesRequest(
                    coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                        coordinates=coordinate,
                        radius=self._search_radius,
                    ),
                    type=_convert_segment_type(segment_type),
                ),
            )
        except grpc.aio.AioRpcError as err:
            raise _PlaceNotFoundError from err

        return coordinate.SerializeToString(deterministic=True), response.place


def _convert_segment_type(
    segment_type: segment_type_pb2.SegmentType.ValueType,
) -> models_pb2.Type.ValueType:
    match segment_type:
        case segment_type_pb2.SEGMENT_TYPE_FLIGHT:
            return models_pb2.Type.TYPE_AIRPORT
        case segment_type_pb2.SEGMENT_TYPE_TRAIN:
            return models_pb2.Type.TYPE_RAILWAY_STATION
        case _:
            return models_pb2.Type.TYPE_UNSPECIFIED
