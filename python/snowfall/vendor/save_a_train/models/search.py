from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from snowfall.vendor.save_a_train import normalizers as save_a_train_normalizers


class Language(BaseModel):
    name: str  # full name, e.g. "English"
    short_name: str = Field(..., alias="value")  # 2 letter code, e.g. "en"


class StationName(BaseModel):
    name: str
    language: Language


class Station(BaseModel):
    uid: str
    names: list[StationName]


class Route(BaseModel):
    origin_station: Station
    destination_station: Station


class SearchResult(BaseModel):
    identifier: int = Field(..., alias="id")
    route: Route
    departure_datetime: datetime
    arrival_datetime: datetime
    duration: timedelta
    best_price: str
    kind_of: str
    changes_count: int

    _normalize_time = save_a_train_normalizers.normalizer(
        ("duration",),
        save_a_train_normalizers.normalize_time,
    )


class SearchResponse(BaseModel):
    identifier: str
    complete: bool
    route: Route
    departure_datetime: datetime
    return_departure_datetime: Optional[datetime]
    expiration_time_left: timedelta
    search_results: list[SearchResult] = Field(..., alias="results")

    _normalize_time = save_a_train_normalizers.normalizer(
        ("expiration_time_left",),
        save_a_train_normalizers.normalize_time,
    )
