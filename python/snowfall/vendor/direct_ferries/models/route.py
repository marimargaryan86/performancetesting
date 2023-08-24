import functools
from collections.abc import Sequence

import timezonefinder
from pydantic import v1 as pydantic

from snowfall.vendor.direct_ferries import enums
from snowfall.vendor.direct_ferries.models import base, operator

_tz_finder = timezonefinder.TimezoneFinder()


class Pet(base.CamelCaseBaseModel):
    pet_type: enums.PetType
    name: str | None
    max_allowed: int | None
    number_of_pets: int | None


class ResidentDiscount(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str | None
    conditions: str | None


class City(base.CamelCaseBaseModel):
    code: str | None
    name: str | None


class DiscountDetails(base.CamelCaseBaseModel):
    resident_discounts: Sequence[ResidentDiscount] | None
    cities: Sequence[City] | None


class Port(base.CamelCaseBaseModel):
    name: str | None
    code: str
    address: str | None
    latitude: float
    longitude: float

    @functools.cached_property
    def timezone(self) -> str:
        timezone_name = _tz_finder.timezone_at(lng=self.longitude, lat=self.latitude)

        if not timezone_name:
            raise RuntimeError("Unable to determine time zone")

        return timezone_name


class Route(base.CamelCaseBaseModel):
    route_id: int
    name: str | None
    is_foot_passenger: bool
    is_vehicle: bool
    port_from: Port
    port_to: Port
    operator_details: operator.OperatorDetails
    discount_details: DiscountDetails
    allow_pets: bool
    pets: Sequence[Pet] | None
    pet_conditions: str | None


class RouteData(base.CamelCaseBaseModel):
    routes: Sequence[Route]


class RouteResponse(base.CamelCaseBaseModel):
    route_data: RouteData = pydantic.Field(..., alias="data")
