from typing import Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    name: Optional[str] = None


class Area(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    name: Optional[str] = None
    city: Optional[City] = None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None
    station_type: Optional[str] = None
    street_and_number: Optional[str] = None
    time_zone: Optional[str] = None
    zip_code: Optional[str] = None
    area: Optional[Area] = None
    city: Optional[City] = None


class StationId(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
