from __future__ import annotations

import abc
import dataclasses
import datetime
import zoneinfo
from collections.abc import Sequence

from google.protobuf import timestamp_pb2

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.duffel.models.offer import Offer


@dataclasses.dataclass(frozen=True)
class Requirement:
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


class Validator:
    @abc.abstractmethod
    def matches(self, offer: Offer) -> bool:
        raise NotImplementedError()


class Validators(Validator):
    def __init__(self, *args: Validator) -> None:
        self.validators = args

    def matches(self, offer: Offer) -> bool:
        return all(validator.matches(offer) for validator in self.validators)


class AirlineValidator(Validator):
    def __init__(
        self,
        enabled_airlines: frozenset[str] | None = None,
        disabled_airlines: frozenset[str] | None = None,
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
