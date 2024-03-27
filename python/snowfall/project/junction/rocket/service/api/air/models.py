import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, alias_generators


class BaseModel(PydanticBase):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Passenger(BaseModel):
    date_of_birth: date


class AirSearchResult(BaseModel):
    id: uuid.UUID


class AirSearchCriteria(BaseModel):
    departure_at: date
    origin: str
    destination: str


class AirSearchAttributes(BaseModel):
    criteria: AirSearchCriteria
    passengers: list[Passenger]


class AirSearchRequestData(BaseModel):
    type: Literal["air-searches"]
    attributes: AirSearchAttributes


class AirSearchRequest(BaseModel):
    data: AirSearchRequestData
