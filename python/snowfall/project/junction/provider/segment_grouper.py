import copy
import datetime
import itertools
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Generic

import more_itertools

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf


@dataclass(frozen=True)
class SubTrip(object):
    trip_id: str
    origins: frozenset[str]
    destinations: frozenset[str]
    departure: datetime.datetime
    arrival: datetime.datetime
    segments: Sequence[models_pb2.Segment]


@dataclass(frozen=True)
class TripCriteria(object):
    outbound: SubTrip
    inbound: SubTrip | None = None

    def get_combinations(self) -> Iterator[tuple[str, str]]:
        return itertools.product(
            self.outbound.origins,
            self.outbound.destinations,
        )


class SegmentGrouper(Generic[h3.MappedValue]):
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[h3.MappedValue],
        min_lower_bound: datetime.timedelta | None = None,
    ):
        self._h3_mapping = h3_mapping
        self._min_lower_bound = min_lower_bound

    def trips_to_sub_trips(
        self,
        trips: Iterable[models_pb2.Trip],
        type_filter: models_pb2.Schedule.Type.ValueType,
    ) -> Iterator[SubTrip]:
        for trip in trips:
            yield from self._trip_to_sub_trips(trip, type_filter)

    def _trip_to_sub_trips(  # noqa: WPS231
        self,
        trip: models_pb2.Trip,
        type_filter: models_pb2.Schedule.Type.ValueType,
    ) -> Iterator[SubTrip]:
        segments: list[models_pb2.Segment] = []

        for segment in trip.segments:
            leg = more_itertools.first(segment.legs)
            if leg.type != type_filter:
                if segments:
                    yield from self._create_sub_trip(trip=trip, segments=segments)
                    segments.clear()

                continue

            if self._min_lower_bound:
                departure_at = protobuf.protobuf_to_datetime(
                    leg.departure_at,
                )
                time_delta = departure_at - datetime.datetime.now(datetime.UTC)
                if time_delta <= self._min_lower_bound:
                    continue

            segments.append(segment)

        if segments:
            yield from self._create_sub_trip(trip=trip, segments=segments)

    def _find_leg(  # noqa: WPS231
        self,
        segments: Sequence[models_pb2.Segment],
        *,
        origin: bool,
    ) -> tuple[set[h3.MappedValue], models_pb2.Leg | None]:
        locations: set[h3.MappedValue] = set()
        found_leg = None
        while segments and not locations:
            legs = segments[0].legs if origin else segments[-1].legs[::-1]
            for leg in legs:
                points = leg.origin if origin else leg.destination
                locations = self._h3_mapping.find_mapped_values(
                    coordinates=points.coordinates,
                    neighbour_search_radius=1,
                )
                if locations:
                    found_leg = leg
                    break
            if not locations:
                segments = segments[1:] if origin else segments[:-1]
        return locations, found_leg

    def _create_sub_trip(
        self,
        trip: models_pb2.Trip,
        segments: Sequence[models_pb2.Segment],
    ) -> Iterator[SubTrip]:
        origins, first_leg = self._find_leg(segments, origin=True)
        destinations, last_leg = self._find_leg(segments, origin=False)

        if not origins or not destinations:
            return
        assert first_leg is not None  # noqa: S101
        assert last_leg is not None  # noqa: S101

        yield SubTrip(
            trip_id=trip.id,
            departure=protobuf.protobuf_to_datetime(
                first_leg.departure_at,
            ).astimezone(more_itertools.first(origins).timezone),
            arrival=protobuf.protobuf_to_datetime(
                last_leg.arrival_at,
            ).astimezone(more_itertools.first(destinations).timezone),
            origins=frozenset(origin.identifier for origin in origins),
            destinations=frozenset(
                destination.identifier for destination in destinations
            ),
            segments=copy.deepcopy(segments),
        )


def generate_trip_criteria(
    sub_trips: Iterable[SubTrip],
) -> Iterator[TripCriteria]:
    remaining_trips = sorted(sub_trips, key=lambda trip: trip.departure)

    while len(remaining_trips):
        outbound = remaining_trips.pop(0)
        inbound = _find_return_trip(outbound, remaining_trips)

        if inbound:
            yield TripCriteria(outbound=outbound, inbound=inbound)

        yield TripCriteria(outbound=outbound)


def _find_return_trip(
    outbound: SubTrip,
    possible_inbounds: Sequence[SubTrip],
) -> SubTrip | None:
    for possible_inbound in possible_inbounds:
        if _is_inbound_match(outbound, possible_inbound):
            return possible_inbound

    return None


def _is_inbound_match(outbound: SubTrip, possible_inbound: SubTrip) -> bool:
    return (
        outbound.trip_id != possible_inbound.trip_id
        and outbound.origins == possible_inbound.destinations
        and outbound.destinations == possible_inbound.origins
    )
