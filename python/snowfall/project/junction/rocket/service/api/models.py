import uuid
from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, alias_generators


class BaseModel(PydanticBase):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class PlaceType(IntEnum):
    type_unspecified = 0
    type_city = 1
    type_railway_station = 2
    type_airport = 3
    type_ferry_port = 4


class PlaceIdentifier(BaseModel):
    id: uuid.UUID
    name: str
    type: PlaceType


_MAX_LONGITUDE = 180.0
_MIN_LONGITUDE = -180.0
_MAX_LATITUDE = 90.0
_MIN_LATITUDE = -90.0


class LatLng(BaseModel):
    latitude: float = Field(ge=_MIN_LATITUDE, le=_MAX_LATITUDE)
    longitude: float = Field(ge=_MIN_LONGITUDE, le=_MAX_LONGITUDE)


class SearchCapabilities(BaseModel):
    rail: bool
    air: bool
    ferry: bool


class Place(BaseModel):
    id: uuid.UUID
    name: str
    coordinates: LatLng
    time_zone: str
    country_code: str = Field(pattern="[A-Z]{2}")
    country_name: str
    updated_at: datetime
    city: PlaceIdentifier | None
    type: PlaceType
    search_capabilities: SearchCapabilities
    contains: list[PlaceIdentifier]
