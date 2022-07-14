from typing import Optional

import pydantic

from snowfall.vendor.direct_ferries.models import base


class Trailer(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    length: float
    height: float
    description: str


class Vehicle(base.CamelCaseBaseModel):
    type_id: int
    make_model_id: int
    make: int
    model: str
    height: int
    length: int
    additional_height: int
    additional_length: float
    trailer: Optional[Trailer]
    registration: str
