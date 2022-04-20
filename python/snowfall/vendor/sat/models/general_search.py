from datetime import date, time, timedelta
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from snowfall.vendor.sat import normalizers as sat_normalizers


class GeneralTrip(BaseModel):
    origin_station: str
    destin_station: str
    departure_date: date
    departure_time: time
    duration: timedelta
    arrival_date: date
    arrival_time: time
    changes: int
    operator: str
    connections: Optional[str]
    price: dict[str, Decimal]  # fare class: price
    train_numbers: str
    departure_connections: Optional[str]
    arrival_connections: Optional[str]
    layover_connections: Optional[str]

    _normalize_nullable_fields = sat_normalizers.normalizer(
        (
            "connections",
            "departure_connections",
            "arrival_connections",
            "layover_connections",
        ),
        sat_normalizers.normalize_nullable_fields,
    )

    _normalize_time = sat_normalizers.normalizer(
        ("duration",),
        sat_normalizers.normalize_time,
    )


class GeneralSearchResult(BaseModel):
    outbound: list[GeneralTrip]
    inbound: Optional[list[GeneralTrip]]


class GeneralSearchResponse(BaseModel):
    """Search response from Search API."""

    passengers: int
    general_search_result: GeneralSearchResult = Field(..., alias="result")
