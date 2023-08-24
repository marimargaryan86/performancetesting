from datetime import date, time, timedelta

from pydantic.v1 import BaseModel, Field

from snowfall.vendor.save_a_train import normalizers as save_a_train_normalizers


class GeneralTrip(BaseModel):
    origin_station: str
    destin_station: str
    departure_date: date
    departure_time: time
    duration: timedelta
    arrival_date: date
    arrival_time: time
    changes: int | None
    operator: str
    connections: str | None
    price: dict[str, str]  # fare class: price
    train_numbers: str
    departure_connections: str | None
    arrival_connections: str | None
    layover_connections: str | None

    _normalize_nullable_fields = save_a_train_normalizers.normalizer(
        (
            "connections",
            "departure_connections",
            "arrival_connections",
            "layover_connections",
        ),
        save_a_train_normalizers.normalize_nullable_fields,
    )

    _normalize_time = save_a_train_normalizers.normalizer(
        ("duration",),
        save_a_train_normalizers.normalize_time,
    )


class GeneralSearchResult(BaseModel):
    outbound: list[GeneralTrip]
    inbound: list[GeneralTrip] | None


class GeneralSearchResponse(BaseModel):
    """Search response from Search API."""

    passengers: int
    general_search_result: GeneralSearchResult = Field(..., alias="result")
