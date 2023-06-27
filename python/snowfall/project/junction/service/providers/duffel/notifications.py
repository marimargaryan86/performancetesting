import abc
import datetime
from email import message

import aiosmtplib
import more_itertools

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.vendor.duffel.models import order as order_model


class NotificationError(Exception):
    """Raised when an exception occurred during sending."""


class Notification(abc.ABC):
    _template: str

    @property
    def body(self) -> str:
        return self._template.strip().format(**self.template_parameters)

    @property
    @abc.abstractmethod
    def subject(self) -> str:
        """Get subject of the notification."""

    @property
    @abc.abstractmethod
    def template_parameters(self) -> dict[str, str]:
        """Get parameters used in the body template."""


class Notifier(abc.ABC):
    @abc.abstractmethod
    async def send(self, notification: Notification) -> None:
        """Send the notification."""


class SmtpNotifier(Notifier):
    def __init__(
        self,
        smtp_client: aiosmtplib.SMTP,
        sender: str,
        recipient: str,
    ):
        self._client = smtp_client
        self._sender = sender
        self._recipient = recipient

    async def send(self, notification: Notification) -> None:
        email = message.EmailMessage()
        email["From"] = self._sender
        email["To"] = self._recipient
        email["Subject"] = notification.subject
        email.set_content(notification.body)

        async with self._client:
            try:
                await self._client.send_message(email)
            except (
                ValueError,
                aiosmtplib.SMTPResponseException,
                aiosmtplib.SMTPRecipientsRefused,
            ) as error:
                raise NotificationError("Error sending notification") from error


class BookingNotification(Notification):
    _template = """
Reservation created by Junction

Journey ID : {journey_id}
Order ID : {order_id}
Booking ID : {booking_id}
SPNR : {spnr}
Checkin locator (other) : {checkin_pnr}
First name : {first_name}
Last name : {last_name}
Booking date : {created_at}
Travel departure date : {departure_at}
"""

    def __init__(
        self,
        metadata: amqp_pb2.OrderMetadata,
        order: order_model.Order,
    ):
        self._metadata = metadata
        self._order = order

    @property
    def subject(self) -> str:
        return "ACTION REQUIRED : BOOKING {duffel_pnr}".format(
            duffel_pnr=self._order.booking_reference,
        )

    @property
    def template_parameters(self) -> dict[str, str]:
        first_passenger = more_itertools.first(self._order.passengers or [])
        first_segment = more_itertools.first(self._order.slices[0].segments or [])

        return {
            "journey_id": self._metadata.journey_id,
            "order_id": self._metadata.order_id,
            "booking_id": self._metadata.booking_id,
            "spnr": self._metadata.passenger_name_record,
            "checkin_pnr": self._order.booking_reference or "",
            "first_name": first_passenger.given_name or "",
            "last_name": first_passenger.family_name or "",
            "created_at": datetime.datetime.now(
                tz=datetime.UTC,
            ).isoformat(timespec="seconds"),
            "departure_at": (
                first_segment.departing_at.isoformat(timespec="seconds") or ""
            ),
        }
