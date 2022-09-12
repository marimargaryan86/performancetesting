import abc
import datetime
from email import message

import aiosmtplib
import more_itertools
import structlog

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2
from snowfall.vendor.ask2go.models import booking as a2g_booking


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


class BookingNotification(Notification):
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


class Notifier(abc.ABC):
    @abc.abstractmethod
    async def send(self, notification: Notification) -> None:
        """Send the notification."""


class LogNotifier(Notifier):
    def __init__(self) -> None:
        self._logger = structlog.get_logger(__name__)

    async def send(self, notification: Notification) -> None:
        self._logger.info("Booking created", **notification.template_parameters)


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
            except Exception as error:
                raise NotificationError("Error sending notification") from error
