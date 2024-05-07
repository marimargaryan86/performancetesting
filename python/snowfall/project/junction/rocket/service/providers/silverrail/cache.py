import datetime
import json
import typing
from collections.abc import Sequence

from pydantic import v1 as pydantic
from pydantic.v1 import Protocol, StrBytes

from snowfall.project.junction.go.v1 import models_pb2 as go_models
from snowfall.project.junction.rocket.service.providers.silverrail import (
    criteria,
    xml_serialization,
)
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord
from snowfall.vendor.silverrail.models import booking, shopping

T = typing.TypeVar("T")  # noqa: WPS111
Model = typing.TypeVar("Model", bound=pydantic.BaseModel)


class QuoteNotFoundError(Exception):
    """Raised when quote is not found in the cache."""


class Coordinates(RedisRecord):
    latitude: float
    longitude: float


class RailResultDetail(RedisRecord):
    origin: str
    destination: str
    outbound_departure_after: datetime.datetime
    outbound_departure_before: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    cabin_class: go_models.CabinClass.Type.ValueType


class ResultDetailCache(RedisRepository[RailResultDetail]):
    """Stores search result in the cache."""

    _record_type: type[RailResultDetail] = RailResultDetail


class PriceQuote(RedisRecord):
    """Stores price quotes in the cache."""

    class Config:
        arbitrary_types_allowed = True
        json_encoders: typing.ClassVar = {
            shopping.LegSolutionType: xml_serialization.serialize,
            shopping.PointToPointPriceType: xml_serialization.serialize,
            shopping.PointToPointShoppingResponseType.Results.Passengers: xml_serialization.serialize,
        }

    leg_solution: shopping.LegSolutionType
    ptp_price: shopping.PointToPointPriceType
    passengers: shopping.PointToPointShoppingResponseType.Results.Passengers

    @property
    def booking_leg_solution(self) -> booking.LegSolutionType:
        return xml_serialization.parse_xml(
            xml_serialization.serialize(self.leg_solution),
            booking.LegSolutionType,
        )

    @property
    def booking_ptp_price(self) -> booking.PointToPointPriceType:
        return xml_serialization.parse_xml(
            xml_serialization.serialize(self.ptp_price),
            booking.PointToPointPriceType,
        )

    @classmethod
    def parse_raw(
        cls: type["Model"],
        b: StrBytes,  # noqa: WPS111
        *,
        content_type: str | None = None,
        encoding: str = "utf8",
        proto: Protocol | None = None,
        allow_pickle: bool = False,
    ) -> "Model":
        data = json.loads(b)
        data["leg_solution"] = xml_serialization.parse_xml(
            data["leg_solution"],
            shopping.LegSolutionType,
        )
        data["ptp_price"] = xml_serialization.parse_xml(
            data["ptp_price"],
            shopping.PointToPointPriceType,
        )
        data["passengers"] = xml_serialization.parse_xml(
            data["passengers"],
            shopping.PointToPointShoppingResponseType.Results.Passengers,
        )
        return cls(**data)


class QuoteCache(RedisRepository[PriceQuote]):
    """Stores pricing details in the cache."""

    _record_type: type[PriceQuote] = PriceQuote


def generate_cache_key(search: criteria.Criteria) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search.origin),
                str(search.destination),
            ),
        ),
    )
