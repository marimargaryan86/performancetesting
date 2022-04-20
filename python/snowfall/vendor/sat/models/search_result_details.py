from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from snowfall.vendor.sat.models.search import StationName


class Train(BaseModel):
    category: str
    number: str


class SearchResultTransferChange(BaseModel):
    origin_station_names: list[StationName]
    destination_station_names: list[StationName]
    origin_station_sat_uid: str
    destination_station_sat_uid: str
    departure_datetime: datetime
    arrival_datetime: datetime
    train: Train
    transport_type: str = Field(..., alias="type")


class SearchResultTransferFare(BaseModel):
    identifier: int = Field(..., alias="id")
    name: str
    price: Decimal


class SearchResultTransfer(BaseModel):
    identifier: int = Field(..., alias="id")
    changes: list[SearchResultTransferChange]
    fares: list[SearchResultTransferFare]


class SearchResultDetails(BaseModel):
    result_id: int
    search_identifier: str
    transfers: list[SearchResultTransfer]
