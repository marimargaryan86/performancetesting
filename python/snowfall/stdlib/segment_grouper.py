import datetime
import itertools
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence

import more_itertools

from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2


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
    inbound: Optional[SubTrip] = None

    def get_combinations(self) -> Iterator[tuple[str, str]]:
        return itertools.product(
            self.outbound.origins,
            self.outbound.destinations,
        )


class SegmentGrouper(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[h3.MappedValue]):
        self._h3_mapping = h3_mapping

    def trips_to_sub_trips(
        self,
        trips: Iterable[models_pb2.Trip],
        type_filter: models_pb2.Schedule.Type.ValueType,
    ) -> Iterable[SubTrip]:
        for trip in trips:
            yield from self._trip_to_sub_trips(trip, type_filter)

    def _trip_to_sub_trips(
        self,
        trip: models_pb2.Trip,
        type_filter: models_pb2.Schedule.Type.ValueType,
    ) -> Iterable[SubTrip]:
        segments: list[models_pb2.Segment] = []

        for segment in trip.segments:
            if more_itertools.first(segment.legs).type != type_filter:
                if segments:
                    yield self._create_sub_trip(trip=trip, segments=segments)
                    segments.clear()

                continue

            segments.append(segment)

        if segments:
            yield self._create_sub_trip(trip=trip, segments=segments)

    def _create_sub_trip(
        self,
        trip: models_pb2.Trip,
        segments: Sequence[models_pb2.Segment],
    ) -> SubTrip:
        first_leg = more_itertools.first(more_itertools.first(segments).legs)
        last_leg = more_itertools.last(more_itertools.last(segments).legs)

        origins = self._h3_mapping.find_mapped_values(
            coordinates=first_leg.origin.coordinates,
            neighbour_search_radius=1,
        )
        destinations = self._h3_mapping.find_mapped_values(
            coordinates=last_leg.destination.coordinates,
            neighbour_search_radius=1,
        )

        return SubTrip(
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
            segments=segments,
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
