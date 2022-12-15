from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Qta(KarhooBaseModel):
    high_minutes: int
    low_minutes: int


class Vehicles(KarhooBaseModel):
    classes: list[str] | None
    tags: list[str] | None
    types: list[str] | None


class Vehicle(KarhooBaseModel):
    qta: Qta | None
    type: Literal["moto", "standard", "mpv", "bus"]  # noqa: A003
    passenger_capacity: int | None
    luggage_capacity: int | None
    tags: list[
        Literal[
            "electric",
            "hybrid",
            "wheelchair",
            "child-seat",
            "executive",
            "luxury",
        ]
    ]
    vehicle_list: list[str] | None
    image: str | None
