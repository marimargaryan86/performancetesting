import datetime
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence

import more_itertools

from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2


@dataclass(frozen=True)
class SubTrip(object):
    trip_id: str
    origins: Sequence[str]
    destinations: Sequence[str]
    departure: datetime.datetime
    arrival: datetime.datetime
    segments: Sequence[models_pb2.Segment]


@dataclass(frozen=True)
class SegmentDetails(object):
    segment: models_pb2.Segment
    origin: str
    destination: str
    departure: datetime.datetime
    arrival: datetime.datetime


@dataclass(frozen=True)
class TripDetails(object):
    is_return_trip: bool
    outbound_segment: models_pb2.Segment
    inbound_segment: Optional[models_pb2.Segment]
    origin: str
    destination: str
    outbound_departure: datetime.datetime
    outbound_arrival: datetime.datetime
    inbound_departure: Optional[datetime.datetime]
    inbound_arrival: Optional[datetime.datetime]


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
            origins=[origin.identifier for origin in origins],
            destinations=[destination.identifier for destination in destinations],
            segments=segments,
        )


# todo: refactor this, probably remove it also
def generate_trips(
    segments: Sequence[SegmentDetails],
) -> Iterator[TripDetails]:
    for segment_i, outbound_segment in enumerate(segments):
        for inbound_segment in segments[segment_i + 1 :]:
            segments_form_a_return_trip = (
                outbound_segment.origin == inbound_segment.destination
                and outbound_segment.destination == inbound_segment.origin
            )
            if segments_form_a_return_trip:
                yield TripDetails(
                    is_return_trip=True,
                    outbound_segment=outbound_segment.segment,
                    inbound_segment=inbound_segment.segment,
                    origin=outbound_segment.origin,
                    destination=outbound_segment.destination,
                    outbound_departure=outbound_segment.departure,
                    outbound_arrival=outbound_segment.arrival,
                    inbound_departure=inbound_segment.departure,
                    inbound_arrival=inbound_segment.arrival,
                )

        yield TripDetails(
            is_return_trip=False,
            outbound_segment=outbound_segment.segment,
            inbound_segment=None,
            origin=outbound_segment.origin,
            destination=outbound_segment.destination,
            outbound_departure=outbound_segment.departure,
            outbound_arrival=outbound_segment.arrival,
            inbound_departure=None,
            inbound_arrival=None,
        )
