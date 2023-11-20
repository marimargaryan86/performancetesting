import dataclasses
from collections.abc import Sequence


@dataclasses.dataclass(frozen=True)
class Price(object):
    amount: str
    currency: str


@dataclasses.dataclass(frozen=True)
class Leg(object):
    origin_name: str
    destination_name: str
    departure_date: str


@dataclasses.dataclass(frozen=True)
class Segment(object):
    operator: str
    legs: Sequence[Leg]


@dataclasses.dataclass(frozen=True)
class OperatorBookingReference(object):
    operator_booking_reference: str


@dataclasses.dataclass(frozen=True)
class Booking(object):
    booking_id: str
    price: Price
    provider_name: str
    trip_reference: str
    operator_booking_references: Sequence[OperatorBookingReference]
    trip_options: Sequence[Segment]


@dataclasses.dataclass(frozen=True)
class Passengers(object):
    first_name: str
    last_name: str


@dataclasses.dataclass(frozen=True)
class Order(object):
    order_id: str
    passengers: Sequence[Passengers]


@dataclasses.dataclass(frozen=True)
class Journey(object):
    reseller_id: str
    passenger_name_record: str
