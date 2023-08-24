from pydantic import v1 as pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    name: str | None


class Area(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    name: str | None
    city: City | None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    latitude: float | None
    longitude: float | None
    name: str | None
    station_type: str | None
    street_and_number: str | None
    time_zone: str | None
    zip_code: str | None
    area: Area | None
    city: City | None


class StationId(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
