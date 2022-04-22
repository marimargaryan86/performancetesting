from __future__ import annotations

import dataclasses
import datetime
import zoneinfo
from typing import Sequence

from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


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


def from_segments(segments: Sequence[models_pb2.Segment]) -> Requirements:
    return [Requirement.from_leg(leg) for segment in segments for leg in segment.legs]
