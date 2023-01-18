from __future__ import annotations

import abc
import dataclasses
import datetime
import zoneinfo
from typing import AbstractSet, Sequence

import structlog
from google.protobuf import timestamp_pb2

from snowfall.project.junction.service.providers.duffel.search import parser
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


class Validator(object):
    @abc.abstractmethod
    def matches(self, offer: Offer) -> bool:
        raise NotImplementedError()


class Validators(Validator):
    def __init__(self, *args: Validator) -> None:
        self.validators = args

    def matches(self, offer: Offer) -> bool:
        return all((validator.matches(offer) for validator in self.validators))


class AirlineValidator(Validator):
    def __init__(
        self,
        enabled_airlines: AbstractSet[str] | None = None,
        disabled_airlines: AbstractSet[str] | None = None,
    ) -> None:
        self._enabled_airlines = enabled_airlines
        self._disabled_airlines = disabled_airlines

    def matches(self, offer: Offer) -> bool:
        if not self._enabled_airlines and not self._disabled_airlines:
            return True

        for offer_slice in offer.slices:
            for segment in offer_slice.segments or []:
                airline = segment.marketing_carrier.iata_code

                if not self._airline_matches(airline):
                    return False

        return True

    def _airline_enabled(self, airline: str) -> bool:
        if not self._enabled_airlines:
            return True

        return airline in self._enabled_airlines

    def _airline_disabled(self, airline: str) -> bool:
        if not self._disabled_airlines:
            return False

        return airline in self._disabled_airlines

    def _airline_matches(self, airline: str | None) -> bool:
        if not airline:
            return False

        return self._airline_enabled(airline) and not self._airline_disabled(airline)


class OfferValidator(Validator):
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
        if not offer.slices:
            return False

        slice_segments = [  # noqa: WPS224
            leg
            for offer_slice in offer.slices
            for segment in offer_slice.segments or []
            for leg in parser.segment_to_legs(segment)
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
