import datetime

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.provider import notifications
from snowfall.vendor.karhoo.models import bookings


class BookingNotification(notifications.Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
SPNR : {spnr}
Booking date : {created_at}
Follow code : {follow_code}
Pickup date : {pickup_date}
Pickup point latitude : {pickup_point_latitude}
Pickup point longitude : {pickup_point_longitude}
Start location : {origin}
Destination location : {destination}
"""

    def __init__(
        self,
        metadata: amqp_pb2.OrderMetadata,
        booking: bookings.BookingResponse,
    ):
        self._meta_data = metadata
        self._booking = booking

    @property
    def subject(self) -> str:
        return "KARHOO BOOKING : {identifier}".format(
            identifier=self._booking.id,
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        return {
            "journey_id": self._meta_data.journey_id,
            "order_id": self._meta_data.order_id,
            "booking_id": self._meta_data.booking_id,
            "spnr": self._meta_data.passenger_name_record,
            "created_at": datetime.datetime.now(
                tz=datetime.UTC,
            ).isoformat(timespec="seconds"),
            "follow_code": self._booking.follow_code or "",
            "pickup_date": self._booking.date_scheduled or "",
            "pickup_point_latitude": self._booking.origin.position.latitude,
            "pickup_point_longitude": self._booking.origin.position.longitude,
            "origin": self._booking.origin.display_address,
            "destination": self._booking.destination.display_address,
        }
