import datetime
from dataclasses import dataclass
from typing import Iterator, Optional, Sequence

from snowfall.stdlib.v1alpha import models_pb2


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


def generate_potential_return_trips(
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
