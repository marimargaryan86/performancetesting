from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Driver(KarhooBaseModel):
    first_name: str
    last_name: str
    phone_number: str
    photo_url: str | None
    license_number: str | None


class VehicleAttributes(KarhooBaseModel):
    passenger_capacity: int | None
    luggage_capacity: int | None
    hybrid: bool | None
    electric: bool | None
    child_seat: bool | None


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
