import dataclasses


@dataclasses.dataclass(frozen=True)
class Ticket:
    journey_id: str
    order_id: str
    booking_id: str
    br_booking_id: str
    br_dnr: str
    passenger_name_record: str
    created_at: str
    departure_at: str
