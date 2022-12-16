import uuid
from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel
from snowfall.vendor.karhoo.models.location import MeetingPoint, Place
from snowfall.vendor.karhoo.models.passenger import Passenger
from snowfall.vendor.karhoo.models.price import Fare
from snowfall.vendor.karhoo.models.quotes import Fleet, Quote, ServiceLevelAgreements
from snowfall.vendor.karhoo.models.vehicle import BookingVehicle


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
    id: uuid.UUID  # noqa: A003
    quote_id: uuid.UUID
    passengers: Passenger
    partner_trip_id: str | None
    flight_number: str | None
    train_number: str | None
    cost_center_reference: str | None
    comments: str | None
    train_time: str | None


class RequestBookingResponse(KarhooBaseModel):
    id: uuid.UUID  # noqa: A003
    passengers: Passenger
    partner_traveller_id: str
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
    quote: Quote
    fare: Fare
    external_trip_id: str | None
    display_trip_id: str | None
    fleet: Fleet
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
    train_time: str | None
    service_level_agreements: ServiceLevelAgreements | None
