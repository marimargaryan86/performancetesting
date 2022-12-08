from __future__ import annotations

import dataclasses
import datetime
import zoneinfo
from typing import Sequence

import structlog
from google.protobuf import timestamp_pb2

from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.duffel.models.offer import Offer
from snowfall.vendor.duffel.models.offer_slice import OfferSliceSegment


@dataclasses.dataclass(frozen=True)
class Requirement(object):
    departure_at: datetime.datetime
    arrival_at: datetime.datetime

    @classmethod
    def from_leg(cls, leg: models_pb2.Leg) -> Requirement:
        origin_tz = zoneinfo.ZoneInfo(leg.origin.time_zone)
        destination_tz = zoneinfo.ZoneInfo(leg.destination.time_zone)

        return cls(
            departure_at=cls.to_local_datetime(leg.departure_at, origin_tz),
            arrival_at=cls.to_local_datetime(leg.arrival_at, destination_tz),
        )

    @classmethod
    def to_local_datetime(
        cls,
        timestamp: timestamp_pb2.Timestamp,
        timestamp_tz: zoneinfo.ZoneInfo,
    ) -> datetime.datetime:
        utc_datetime = protobuf.protobuf_to_datetime(timestamp)
        return utc_datetime.astimezone(timestamp_tz).replace(tzinfo=None)


Requirements = Sequence[Requirement]


class OfferValidator(object):
    def __init__(self, requirements: Requirements) -> None:
        self._logger = structlog.get_logger(__name__)
        self._requirements = requirements

    @classmethod
    def from_segments(cls, segments: Sequence[models_pb2.Segment]) -> OfferValidator:
        return cls(
            requirements=[
                Requirement.from_leg(leg)
                for segment in segments
                for leg in segment.legs
            ],
        )

    def matches(self, offer: Offer) -> bool:
        if not offer or not offer.slices:
            return False

        slice_segments = [
            segment
            for offer_slice in offer.slices
            for segment in offer_slice.segments or []
            # todo handle stops
        ]

        if len(self._requirements) != len(slice_segments):
            return False  # make sure all requirements are matched

        for segment_index, segment in enumerate(slice_segments):
            requirement = self._requirements[segment_index]

            if not self._segment_in_requirements(segment, requirement):
                return False

        return True

    def _segment_in_requirements(
        self,
        segment: OfferSliceSegment,
        requirement: Requirement,
    ) -> bool:
        if not segment.departing_at or not segment.arriving_at:
            return False

        if not segment.origin or not segment.destination:
            return False

        if segment.departing_at != requirement.departure_at:
            self._logger.debug(
                "Departure times do not match",
                origin=segment.origin.iata_code,
                destination=segment.destination.iata_code,
                requirement_departure_at=requirement.departure_at.isoformat(),
                offer_departure_at=segment.departing_at.isoformat(),
            )

            return False

        if segment.arriving_at != requirement.arrival_at:
            self._logger.debug(
                "Arrival times do not match",
                origin=segment.origin.iata_code,
                destination=segment.destination.iata_code,
                requirement_arrival_at=requirement.arrival_at.isoformat(),
                offer_arrival_at=segment.arriving_at.isoformat(),
            )

            return False

        return True
