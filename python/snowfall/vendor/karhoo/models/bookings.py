import datetime
import uuid
from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel
from snowfall.vendor.karhoo.models.location import MeetingPoint, Place
from snowfall.vendor.karhoo.models.passenger import Passengers
from snowfall.vendor.karhoo.models.price import Fare
from snowfall.vendor.karhoo.models.quotes import ServiceLevelAgreements
from snowfall.vendor.karhoo.models.vehicle import Driver, VehicleAttributes


class BookingCancellation(KarhooBaseModel):
    reason: Literal[
        "OTHER_USER_REASON",
        "DRIVER_DIDNT_SHOW_UP",
        "ETA_TOO_LONG",
        "DRIVER_IS_LATE",
        "CAN_NOT_FIND_VEHICLE",
        "NOT_NEEDED_ANYMORE",
        "ASKED_BY_DRIVER_TO_CANCEL",
        "FOUND_BETTER_PRICE",
        "NOT_CLEAR_MEETING_INSTRUCTIONS",
        "COULD_NOT_CONTACT_CARRIER",
    ]
    explanation: str | None


class Agent(KarhooBaseModel):
    user_id: str | None
    user_name: str | None
    organisation_id: str | None
    organisation_name: str | None


class CancelledBy(KarhooBaseModel):
    first_name: str | None
    last_name: str | None
    id: str | None  # noqa: A003
    email: str | None


class Booking(KarhooBaseModel):
    meta: dict[str, str] | None
    quote_id: str
    passengers: Passengers
    partner_trip_id: str | None
    flight_number: str | None
    train_number: str | None
    cost_center_reference: str | None
    comments: str | None
    train_time: str | None


class BookingVehicle(KarhooBaseModel):
    vehicle_class: str
    description: str | None
    vehicle_license_plate: str
    driver: Driver
    attributes: VehicleAttributes


class BookingQuote(KarhooBaseModel):
    type: Literal[  # noqa: A003
        "QUOTE_TYPE_NOT_SET",
        "FIXED",
        "METERED",
        "ESTIMATED",
    ] | None
    currency: str
    gratuity_percent: int | None
    vehicle_class: str | None
    qta_high_minutes: int | None
    qta_low_minutes: int | None
    vehicle_attributes: VehicleAttributes
    source: Literal["FLEET", "MARKET"] | None
    high_price: int | None
    low_price: int | None


class BookingFleet(KarhooBaseModel):
    fleet_id: uuid.UUID | None
    name: str | None
    logo_url: str | None
    description: str | None
    phone_number: str | None
    terms_conditions_url: str | None
    email: str | None


class BookingResponse(KarhooBaseModel):
    id: uuid.UUID  # noqa: A003
    passengers: Passengers
    partner_traveller_id: str | None
    status: Literal[
        "REQUESTED",
        "CONFIRMED",
        "DRIVER_EN_ROUTE",
        "ARRIVED",
        "POB",
        "COMPLETED",
        "NO_DRIVERS_AVAILABLE",
        "DRIVER_CANCELLED",
        "BOOKER_CANCELLED",
        "KARHOO_CANCELLED",
        "FAILED",
        "PREAUTH_DECLINED",
        "INCOMPLETE",
    ]
    state_details: str | None
    origin: Place
    destination: Place
    date_scheduled: str | None
    quote: BookingQuote
    fare: Fare
    external_trip_id: str | None
    display_trip_id: str | None
    fleet_info: BookingFleet
    vehicle: BookingVehicle
    partner_trip_id: str | None
    comments: str | None
    flight_number: str | None
    train_number: str | None
    date_booked: str | None
    meeting_point: MeetingPoint
    agent: Agent | None
    cost_centre_reference: str | None
    cancelled_by: CancelledBy | None
    follow_code: str | None
    meta: dict[str, str] | None
    train_time: datetime.datetime | None
    service_level_agreements: ServiceLevelAgreements | None
