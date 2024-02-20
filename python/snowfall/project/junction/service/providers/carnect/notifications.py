import datetime
from email.mime import multipart, text

import aiosmtplib

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.providers.carnect import adapter
from snowfall.vendor.carnect.adapters import reservation_adapter


class EmailNotificationError(Exception):
    """General error while sending email notification."""


class BookingNotification(notifications.Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
SPNR : {spnr}
Booking date : {created_at}
Pickup date : {pickup_date}
Drop off date : {drop_off_date}
Start location : {origin}
Destination location : {destination}
"""

    def __init__(
        self,
        metadata: amqp_pb2.OrderMetadata,
        res_adapter: reservation_adapter.ReservationAdapter,
    ):
        self._meta_data = metadata
        self._res_adapter = res_adapter

    @property
    def subject(self) -> str:
        return "CARNECT BOOKING : {identifier}".format(
            identifier=self._res_adapter.get_id_context(),
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        reservation = self._res_adapter.reservation()
        pickup_date = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.pick_up_date_time",
            "N/A",
        )
        drop_off_date = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.return_date_time",
            "N/A",
        )
        pick_up_location = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.pick_up_location",
            "N/A",
        )
        origin = pick_up_location[0].value if pick_up_location else "N/A"
        destination = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.return_location.value",
            "N/A",
        )
        return {
            "journey_id": self._meta_data.journey_id,
            "order_id": self._meta_data.order_id,
            "booking_id": self._meta_data.booking_id,
            "spnr": self._meta_data.passenger_name_record,
            "created_at": datetime.datetime.now(
                tz=datetime.UTC,
            ).isoformat(timespec="seconds"),
            "pickup_date": pickup_date,
            "drop_off_date": drop_off_date,
            "origin": origin,
            "destination": destination,
        }


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP, sender: str):
        self._smtp = client
        self._sender = sender

    async def send_email_html_template(
        self,
        mail_to: str,
        subject: str,
        body: str,
    ) -> None:
        email = multipart.MIMEMultipart("alternative")
        email["From"] = self._sender
        email["To"] = mail_to
        email["Subject"] = subject
        email.attach(text.MIMEText(body, "html", "utf-8"))

        try:
            async with self._smtp:
                await self._smtp.send_message(email)
        except (ValueError, aiosmtplib.errors.SMTPException) as error:
            raise EmailNotificationError from error
