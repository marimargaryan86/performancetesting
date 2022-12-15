import datetime

from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import models


class BookingNotification(notifications.Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
SPNR : {spnr}
Search Identifier : {search_identifier}
Ticket Confirmation Code : {confirmation_code}
Ticket PDF URL : {ticket_url}
Booking date : {created_at}
Travel departure date : {departure_at}
"""

    def __init__(
        self,
        metadata: amqp_pb2.OrderMetadata,
        booking: models.CombinedBookingResults,
    ):
        self._metadata = metadata
        self._booking = booking

    @property
    def subject(self) -> str:
        return "SAT BOOKING : {identifier}".format(
            identifier=self._booking.get_ticket.confirmation_code,
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        booking = self._booking.make_booking

        return {
            "journey_id": self._metadata.journey_id,
            "order_id": self._metadata.order_id,
            "booking_id": self._metadata.booking_id,
            "spnr": self._metadata.passenger_name_record,
            "search_identifier": booking.search_identifier,
            "confirmation_code": self._booking.get_ticket.confirmation_code,
            "ticket_url": self._booking.get_ticket.url,
            "created_at": datetime.datetime.now(
                tz=datetime.timezone.utc,
            ).isoformat(timespec="seconds"),
            "departure_at": booking.outbound_trip_info.departure.isoformat(
                timespec="seconds",
            ),
        }
