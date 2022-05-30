from __future__ import annotations

import dataclasses
import datetime
import types
import zoneinfo
from typing import Optional, Sequence

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.orders.v1alpha import models_pb2 as orders_models
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go.models import common

_CABIN_MAPPING = types.MappingProxyType(
    {
        "Economy": models_pb2.CabinClass.TYPE_ECONOMY,
        "EconomyWithRestrictions": models_pb2.CabinClass.TYPE_ECONOMY,
        "EconomyWithoutRestrictions": models_pb2.CabinClass.TYPE_ECONOMY,
        "PremiumEconomy": models_pb2.CabinClass.TYPE_PREMIUM,
        "Business": models_pb2.CabinClass.TYPE_BUSINESS,
        "PremiumBusiness": models_pb2.CabinClass.TYPE_BUSINESS,
        "First": models_pb2.CabinClass.TYPE_FIRST,
    },
)


def cabin_to_proto(cabin: Optional[str]) -> models_pb2.CabinClass.Type.V:
    if cabin is None:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED

    try:
        return _CABIN_MAPPING[cabin]
    except KeyError:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED


def gender_from_proto(gender: orders_models.Passenger.Gender.V) -> common.Gender:
    if gender == orders_models.Passenger.GENDER_MALE:
        return common.Gender.male
    elif gender == orders_models.Passenger.GENDER_FEMALE:
        return common.Gender.female
    return common.Gender.unknown


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
