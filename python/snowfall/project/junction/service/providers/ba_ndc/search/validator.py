from __future__ import annotations

import dataclasses
import datetime
import zoneinfo
from typing import Mapping, Sequence

import structlog
from google.protobuf import timestamp_pb2

from snowfall.project.junction.service.providers.ba_ndc.search import parser
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.ba_ndc.models import response_common_offer_schemas
from snowfall.vendor.ba_ndc.models.response_offer_search_schemas import Offer


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
    def __init__(
        self,
        requirements: Requirements,
        ba_ndc_segments: Mapping[str, response_common_offer_schemas.Segment],
    ) -> None:
        self._logger = structlog.get_logger(__name__)
        self._requirements = requirements
        self._ba_ndc_segments = ba_ndc_segments

    @classmethod
    def from_segments(
        cls,
        segments: Sequence[models_pb2.Segment],
        ba_ndc_segments: Mapping[str, response_common_offer_schemas.Segment],
    ) -> OfferValidator:
        return cls(
            requirements=[
                Requirement.from_leg(leg)
                for segment in segments
                for leg in segment.legs
            ],
            ba_ndc_segments=ba_ndc_segments,
        )

    def matches(self, offer: Offer) -> bool:
        if not offer.trips:
            return False

        legs = self._get_legs_from_offer(offer)

        if len(self._requirements) != len(legs):
            return False  # make sure all requirements are matched

        for segment_index, segment in enumerate(legs):
            requirement = self._requirements[segment_index]

            if not self._segment_in_requirements(  # noqa: WPS337
                segment,
                requirement,
            ):
                return False

        return True

    def _segment_in_requirements(
        self,
        segment: response_common_offer_schemas.Segment,
        requirement: Requirement,
    ) -> bool:
        if segment.departure_date_time != requirement.departure_at:
            self._logger.debug(
                "Departure times do not match",
                origin=segment.origin.code,
                destination=segment.destination.code,
                requirement_departure_at=requirement.departure_at.isoformat(),
                offer_departure_at=segment.departure_date_time.isoformat(),
            )

            return False

        if segment.arrival_date_time != requirement.arrival_at:
            self._logger.debug(
                "Arrival times do not match",
                origin=segment.origin.code,
                destination=segment.destination.code,
                requirement_arrival_at=requirement.arrival_at.isoformat(),
                offer_arrival_at=segment.arrival_date_time.isoformat(),
            )

            return False

        return True

    def _get_legs_from_offer(
        self,
        offer: Offer,
    ) -> list[response_common_offer_schemas.Segment]:
        legs: list[response_common_offer_schemas.Segment] = []

        for trip in offer.trips:
            for segment_id in trip.segment_ids:
                ndc_segment = self._ba_ndc_segments.get(segment_id)

                if ndc_segment:
                    legs = legs + list(parser.segment_to_legs(ndc_segment))

        return legs
