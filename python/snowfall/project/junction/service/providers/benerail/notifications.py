import datetime

from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.providers.benerail.v1 import amqp_pb2


class BookingNotification(notifications.Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
Benerail Booking ID: {br_booking_id}
DNR : {dnr}
SPNR : {spnr}
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
        return "BENERAIL BOOKING : {dnr}".format(
            dnr=self._message.br_dnr,
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        return {
            "journey_id": self._message.journey_id,
            "order_id": self._message.order_id,
            "booking_id": self._message.booking_id,
            "br_booking_id": self._message.br_booking_id,
            "spnr": self._message.passenger_name_record,
            "dnr": self._message.br_dnr,
            "ticket_url": self._message.ticket_url,
            "created_at": datetime.datetime.now(
                tz=datetime.UTC,
            ).isoformat(timespec="seconds"),
            "departure_at": self._message.departure_at,
        }
