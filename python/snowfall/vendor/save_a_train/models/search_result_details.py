from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from snowfall.vendor.save_a_train.models.search import StationName


class Train(BaseModel):
    category: Optional[str]
    number: Optional[str]


class SearchResultTransferChange(BaseModel):
    origin_station_names: list[StationName]
    destination_station_names: list[StationName]
    origin_station_save_a_train_uid: str = Field(..., alias="origin_station_sat_uid")
    destination_station_save_a_train_uid: str = Field(
        ...,
        alias="destination_station_sat_uid",
    )
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
