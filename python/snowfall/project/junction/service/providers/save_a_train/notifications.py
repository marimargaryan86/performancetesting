import datetime

from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2


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
        message: amqp_pb2.BookingNotificationTask,
    ):
        self._message = message

    @property
    def subject(self) -> str:
        return "SAT BOOKING : {identifier}".format(
            identifier=self._message.ticket_confirmation_code,
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        return {
            "journey_id": self._message.journey_id,
            "order_id": self._message.order_id,
            "booking_id": self._message.booking_id,
            "spnr": self._message.passenger_name_record,
            "search_identifier": self._message.search_identifier,
            "confirmation_code": self._message.ticket_confirmation_code,
            "ticket_url": self._message.ticket_url,
            "created_at": datetime.datetime.now(
                tz=datetime.timezone.utc,
            ).isoformat(timespec="seconds"),
            "departure_at": self._message.departure_at,
        }
