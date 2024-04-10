import dataclasses
from collections.abc import Sequence


@dataclasses.dataclass(frozen=True)
class Price:
    amount: str
    currency: str


@dataclasses.dataclass(frozen=True)
class Leg:
    origin_name: str
    destination_name: str
    departure_date: str


@dataclasses.dataclass(frozen=True)
class Segment:
    operator: str
    legs: Sequence[Leg]


@dataclasses.dataclass(frozen=True)
class OperatorBookingReference:
    operator_booking_reference: str


@dataclasses.dataclass(frozen=True)
class Booking:
    booking_id: str
    price: Price
    provider_name: str
    trip_reference: str
    operator_booking_references: Sequence[OperatorBookingReference]
    trip_options: Sequence[Segment]


@dataclasses.dataclass(frozen=True)
class Passengers:
    first_name: str
    last_name: str


@dataclasses.dataclass(frozen=True)
class Order:
    order_id: str
    passengers: Sequence[Passengers]


@dataclasses.dataclass(frozen=True)
class Journey:
    reseller_id: str
    passenger_name_record: str


@dataclasses.dataclass(frozen=True)
class TripOptionDetails:
    origin_name: str
    destination_name: str
    departure_date: str


@dataclasses.dataclass(frozen=True)
class RocketBooking:
    booking_id: str
    price: Price
    provider_name: str
    trip_reference: str
    operator_booking_references: Sequence[OperatorBookingReference]
    trip_option_details: Sequence[TripOptionDetails]
    passengers: Sequence[Passengers]
