from __future__ import annotations

import dataclasses
import datetime
import zoneinfo
from collections.abc import Sequence

import more_itertools

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout


@dataclasses.dataclass(frozen=True)
class Requirement:
    departure_at: datetime.datetime
    departure_tz: zoneinfo.ZoneInfo
    arrival_at: datetime.datetime
    arrival_tz: zoneinfo.ZoneInfo

    @classmethod
    def from_segment(cls, segment: models_pb2.Segment) -> Requirement:
        first_leg = more_itertools.first(segment.legs)
        last_leg = more_itertools.last(segment.legs)
        origin_tz = zoneinfo.ZoneInfo(first_leg.origin.time_zone)
        destination_tz = zoneinfo.ZoneInfo(last_leg.destination.time_zone)

        return cls(
            departure_at=protobuf.protobuf_to_datetime(
                first_leg.departure_at,
            ).astimezone(
                origin_tz,
            ),
            departure_tz=origin_tz,
            arrival_at=protobuf.protobuf_to_datetime(last_leg.arrival_at).astimezone(
                destination_tz,
            ),
            arrival_tz=destination_tz,
        )


class SegmentMatcher:
    def __init__(
        self,
        segments: Sequence[models_pb2.Segment],
        allowed_window_td: datetime.timedelta,
    ) -> None:
        self._segments = segments
        self._logger = stdout.get_logger()
        self._allowed_window_td = allowed_window_td

    def offer_group_matches(self, offer_group: offers_pb2.OfferGroup) -> bool:
        requirements = self._get_requirements()

        if len(self._segments) != len(offer_group.segments):
            return False

        for segment_index, segment in enumerate(offer_group.segments):
            try:
                requirement = requirements[segment_index]
            except IndexError:
                return False

            if not self._segment_in_requirements(segment, requirement):
                return False

        return True

    def _get_requirements(self) -> Sequence[Requirement]:
        return [Requirement.from_segment(segment) for segment in self._segments]

    def _segment_in_requirements(
        self,
        segment: offers_pb2.OfferSegment,
        requirement: Requirement,
    ) -> bool:
        first_leg = more_itertools.first(segment.legs)
        last_leg = more_itertools.last(segment.legs)

        departure_at = protobuf.protobuf_to_datetime(first_leg.departure_at).astimezone(
            zoneinfo.ZoneInfo(first_leg.origin.time_zone),
        )

        if abs(departure_at - requirement.departure_at) > self._allowed_window_td:
            self._logger.debug(
                "Departure times do not match",
                origin=first_leg.origin.name,
                destination=first_leg.destination.name,
                requirement_departure_at=requirement.departure_at.isoformat(),
                offer_departure_at=departure_at.isoformat(),
            )

            return False

        arrival_at = protobuf.protobuf_to_datetime(last_leg.arrival_at).astimezone(
            zoneinfo.ZoneInfo(last_leg.destination.time_zone),
        )

        if abs(arrival_at - requirement.arrival_at) > self._allowed_window_td:
            self._logger.debug(
                "Arrival times do not match",
                origin=last_leg.origin.name,
                destination=last_leg.destination.name,
                requirement_arrival_at=requirement.arrival_at.isoformat(),
                offer_arrival_at=arrival_at.isoformat(),
            )

            return False

        return True
