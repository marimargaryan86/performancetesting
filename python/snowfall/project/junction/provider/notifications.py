import abc
from email import message

import aiosmtplib

from snowfall.stdlib.logging import stdout


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


class LogNotifier(Notifier):
    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def send(self, notification: Notification) -> None:
        self._logger.info("Message sent", **notification.template_parameters)


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
