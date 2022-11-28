from typing import Optional, Sequence

import pydantic

from snowfall.vendor.direct_ferries import enums
from snowfall.vendor.direct_ferries.models import base, operator


class Pet(base.CamelCaseBaseModel):
    pet_type: enums.PetType
    name: Optional[str]
    max_allowed: Optional[int]
    number_of_pets: Optional[int]


class ResidentDiscount(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: Optional[str]
    conditions: Optional[str]


class City(base.CamelCaseBaseModel):
    code: Optional[str]
    name: Optional[str]


class DiscountDetails(base.CamelCaseBaseModel):
    resident_discounts: Optional[Sequence[ResidentDiscount]]
    cities: Optional[Sequence[City]]


class Port(base.CamelCaseBaseModel):
    name: Optional[str]
    code: str
    address: Optional[str]
    latitude: float
    longitude: float


class Route(base.CamelCaseBaseModel):
    route_id: int
    name: Optional[str]
    is_foot_passenger: bool
    is_vehicle: bool
    port_from: Port
    port_to: Port
    operator_details: operator.OperatorDetails
    discount_details: DiscountDetails
    allow_pets: bool
    pets: Optional[Sequence[Pet]]
    pet_conditions: Optional[str]


class RouteData(base.CamelCaseBaseModel):
    routes: Sequence[Route]


class RouteResponse(base.CamelCaseBaseModel):
    route_data: RouteData = pydantic.Field(..., alias="data")
