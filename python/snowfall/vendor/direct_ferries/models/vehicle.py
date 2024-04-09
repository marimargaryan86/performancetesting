from pydantic import v1 as pydantic

from snowfall.vendor.direct_ferries.models import base


class Trailer(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    length: float
    height: float
    description: str


class Vehicle(base.CamelCaseBaseModel):
    type_id: int
    make_model_id: int | None
    make: str | None
    model: str | None
    height: int | None
    length: int | None
    additional_height: int | None
    additional_length: float | None
    trailer: Trailer | None
    registration: str | None
