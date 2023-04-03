import datetime

import more_itertools

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.provider import notifications
from snowfall.vendor.ask2go.models import booking as a2g_booking


class BookingNotification(notifications.Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
SPNR : {spnr}
Record locator (sabre) : {sabre_pnr}
Checkin locator (other) : {checkin_pnr}
First name : {first_name}
Last name : {last_name}
Booking date : {created_at}
Travel departure date : {departure_at}
"""

    def __init__(
        self,
        metadata: amqp_pb2.OrderMetadata,
        booking: a2g_booking.Booking,
    ):
        self._metadata = metadata
        self._booking = booking

    @property
    def subject(self) -> str:
        return "ACTION REQUIRED : BOOKING {sabre_pnr}".format(
            sabre_pnr=more_itertools.first(
                self._booking.information.check_in_locators or [],
            ),
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        first_passenger = more_itertools.first(self._booking.travelers)

        return {
            "journey_id": self._metadata.journey_id,
            "order_id": self._metadata.order_id,
            "booking_id": self._metadata.booking_id,
            "spnr": self._metadata.passenger_name_record,
            "sabre_pnr": ", ".join(self._booking.information.record_locators or []),
            "checkin_pnr": ", ".join(self._booking.information.check_in_locators or []),
            "first_name": first_passenger.get("firstName", ""),
            "last_name": first_passenger.get("lastName", ""),
            "created_at": datetime.datetime.now(
                tz=datetime.timezone.utc,
            ).isoformat(timespec="seconds"),
            "departure_at": more_itertools.first(
                self._booking.air_itinerary.trips,
            ).departure.date_time.isoformat(timespec="seconds"),
        }
