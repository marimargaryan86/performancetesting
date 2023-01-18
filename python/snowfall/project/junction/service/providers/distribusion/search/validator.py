from __future__ import annotations

import dataclasses
import datetime
import zoneinfo
from typing import Sequence

import structlog

from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.distribusion.models import connections


@dataclasses.dataclass(frozen=True)
class Requirement(object):
    departure_at: datetime.datetime
    departure_tz: zoneinfo.ZoneInfo
    arrival_at: datetime.datetime
    arrival_tz: zoneinfo.ZoneInfo

    @classmethod
    def from_leg(cls, leg: models_pb2.Leg) -> Requirement:
        origin_tz = zoneinfo.ZoneInfo(leg.origin.time_zone)
        destination_tz = zoneinfo.ZoneInfo(leg.destination.time_zone)

        return cls(
            departure_at=protobuf.protobuf_to_datetime(leg.departure_at).astimezone(
                origin_tz,
            ),
            departure_tz=origin_tz,
            arrival_at=protobuf.protobuf_to_datetime(leg.arrival_at).astimezone(
                destination_tz,
            ),
            arrival_tz=destination_tz,
        )


Requirements = Sequence[Requirement]


def requirements_from_segments(segments: Sequence[models_pb2.Segment]) -> Requirements:
    return [Requirement.from_leg(leg) for segment in segments for leg in segment.legs]


class ConnectionValidator(object):
    def __init__(self) -> None:
        self._logger = structlog.get_logger(__name__)

    def matches(
        self,
        connection: connections.Connection,
        requirements: Requirements,
    ) -> bool:
        if not connection.segments:
            return False

        if len(requirements) != len(connection.segments):
            return False  # make sure all requirements are matched

        for segment_index, segment in enumerate(connection.segments):
            requirement = requirements[segment_index]

            if not self._segment_in_requirements(segment, requirement):
                return False

        return True

    def _segment_in_requirements(
        self,
        segment: connections.Segment,
        requirement: Requirement,
    ) -> bool:
        if not segment.departure_time or not segment.arrival_time:
            return False

        departure_at = datetime.datetime.fromisoformat(segment.departure_time).replace(
            tzinfo=requirement.departure_tz,
        )

        if departure_at != requirement.departure_at:
            self._logger.debug(
                "Departure times do not match",
                origin=segment.departure_station.code,
                destination=segment.arrival_station.code,
                requirement_departure_at=requirement.departure_at.isoformat(),
                offer_departure_at=departure_at.isoformat(),
            )

            return False

        arrival_at = datetime.datetime.fromisoformat(segment.arrival_time).replace(
            tzinfo=requirement.arrival_tz,
        )

        if arrival_at != requirement.arrival_at:
            self._logger.debug(
                "Arrival times do not match",
                origin=segment.departure_station.code,
                destination=segment.arrival_station.code,
                requirement_arrival_at=requirement.arrival_at.isoformat(),
                offer_arrival_at=arrival_at.isoformat(),
            )

            return False

        return True
