from __future__ import annotations

import dataclasses
import datetime
import types
import zoneinfo
from typing import Sequence

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1alpha import (
    models_pb2 as orders_models,
)
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go.models import common

_PENALTY_TYPE_MAPPING = types.MappingProxyType(
    {
        "Exchange": offers_pb2.Penalty.Type.TYPE_EXCHANGE,
        "Refund": offers_pb2.Penalty.Type.TYPE_REFUND,
    },
)

_APPLICABILITY_TYPE_MAPPING = types.MappingProxyType(
    {
        "Before": offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
        "After": offers_pb2.Penalty.Applicability.APPLICABILITY_AFTER,
    },
)


def penalty_type_to_proto(
    penalty_type: str | None,
) -> offers_pb2.Penalty.Type.ValueType:
    if penalty_type is None:
        return offers_pb2.Penalty.Type.TYPE_UNSPECIFIED

    try:
        return _PENALTY_TYPE_MAPPING[penalty_type]
    except KeyError:
        return offers_pb2.Penalty.Type.TYPE_UNSPECIFIED


def applicability_type_to_proto(
    applicability_type: str | None,
) -> offers_pb2.Penalty.Applicability.ValueType:
    if applicability_type is None:
        return offers_pb2.Penalty.Applicability.APPLICABILITY_UNSPECIFIED

    try:
        return _APPLICABILITY_TYPE_MAPPING[applicability_type]
    except KeyError:
        return offers_pb2.Penalty.Applicability.APPLICABILITY_UNSPECIFIED


def gender_from_proto(
    gender: orders_models.Passenger.Gender.ValueType,
) -> common.Gender:
    if gender == orders_models.Passenger.GENDER_MALE:
        return common.Gender.male
    if gender == orders_models.Passenger.GENDER_FEMALE:
        return common.Gender.female
    return common.Gender.unknown


def document_type_from_proto(
    document_type: orders_models.DocumentDetails.Type.ValueType,
) -> common.DocumentType | None:
    if document_type == orders_models.DocumentDetails.Type.TYPE_PASSPORT:
        return common.DocumentType.passport

    return None


def traveler_document_from_proto(
    traveler_document: orders_models.DocumentDetails,
) -> common.TravelerDocument | None:
    try:
        exp_date = protobuf.protobuf_to_date(traveler_document.exp_date)
    except ValueError:
        return None

    document_type = document_type_from_proto(traveler_document.document_type)

    return (
        common.TravelerDocument(
            document_type=document_type,
            document_number=traveler_document.document_number,
            document_issue_country=traveler_document.issue_county,
            document_exp_date=exp_date,
            nationality=traveler_document.nationality,
        )
        if document_type
        else None
    )


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
