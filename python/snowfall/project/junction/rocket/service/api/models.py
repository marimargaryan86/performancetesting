import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel


class Passenger(BaseModel):
    date_of_birth: date


class AirSearchResult(BaseModel):
    id: uuid.UUID


class AirSearchAttributes(BaseModel):
    date: date
    origin: str
    destination: str
    passengers: list[Passenger]


class AirSearchRequestData(BaseModel):
    type: Literal["searches"]
    attributes: AirSearchAttributes


class AirSearchRequest(BaseModel):
    data: AirSearchRequestData
