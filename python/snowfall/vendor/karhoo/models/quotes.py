import uuid
from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel
from snowfall.vendor.karhoo.models.price import Price
from snowfall.vendor.karhoo.models.vehicle import Vehicle, Vehicles


class Rating(KarhooBaseModel):
    count: int | None
    score: int | None


class FreeCancellation(KarhooBaseModel):
    type: Literal["TimeBeforePickup", "BeforeDriverEnRoute"]  # noqa: A003
    minutes: int | None


class FreeWaitingTime(KarhooBaseModel):
    minutes: int


class ServiceLevelAgreements(KarhooBaseModel):
    free_cancellation: FreeCancellation | None
    free_waiting_time: FreeWaitingTime | None


class Fleet(KarhooBaseModel):
    id: uuid.UUID  # noqa: A003
    name: str
    description: str | None
    rating: Rating | None
    logo_url: str | None
    terms_conditions_url: str | None
    phone_number: str | None
    capabilities: list[
        Literal[
            "gps_tracking",
            "flight_tracking",
            "train_tracking",
            "driver_details",
            "vehicle_details",
        ]
    ]
    email: str | None


class Quote(KarhooBaseModel):
    id: uuid.UUID  # noqa: A003
    price: Price
    pick_up_type: Literal["DEFAULT", "MEET_AND_GREET", "CURB_SIDE", "STAND_BY"] | None
    quote_type: Literal["FIXED", "METERED", "ESTIMATED"]
    source: Literal["FLEET", "MARKET"] | None
    fleet: Fleet
    vehicle: Vehicle | None
    service_level_agreements: ServiceLevelAgreements | None


class Availability(KarhooBaseModel):
    vehicles: Vehicles | None


class RequestQuotesResponse(KarhooBaseModel):
    id: uuid.UUID  # noqa: A003
    availability: Availability
    quotes: list[Quote]
    status: Literal["PROGRESSING", "COMPLETED"]
    validity: int | None
