import abc
import asyncio
import dataclasses
from email import message
from email.mime import multipart, text
from typing import Any

import aiofiles
import aiosmtplib
from jinja2 import Template

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem


class NotificationError(Exception):
    """Raised when an exception occurred during sending."""


class BaseNotification(abc.ABC):
    @property
    @abc.abstractmethod
    def subject(self) -> str:
        """Get subject of the notification."""

    @property
    @abc.abstractmethod
    def template_parameters(self) -> dict[str, Any]:
        """Get parameters used in the body template."""


class Notification(BaseNotification):
    _template: str

    @property
    def body(self) -> str:
        return self._template.strip().format(**self.template_parameters)


class HtmlNotification(BaseNotification):
    _template_path: str
    _template_resource: str

    @property
    async def body(self) -> str:
        async with aiofiles.open(
            filesystem.resource_path(
                self._template_path,
                self._template_resource,
            ),
        ) as template_file:
            template = Template(await template_file.read())

        return template.render(**self.template_parameters)


@dataclasses.dataclass(frozen=True)
class Attachment:
    payload: str
    main_type: str
    sub_type: str
    file_name: str


class Notifier(abc.ABC):
    @abc.abstractmethod
    async def send(
        self,
        notification: Notification,
        sender: str | None = None,
        recipient: str | None = None,
        attachment: Attachment | None = None,
    ) -> None:
        """Send the notification."""

    @abc.abstractmethod
    async def send_html(
        self,
        notification: HtmlNotification,
        sender: str | None = None,
        recipient: str | None = None,
    ) -> None:
        """Send the HTML notification."""


class LogNotifier(Notifier):
    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def send(
        self,
        notification: Notification,
        sender: str | None = None,
        recipient: str | None = None,
        attachment: Attachment | None = None,
    ) -> None:
        self._logger.info("Message sent", **notification.template_parameters)

    async def send_html(
        self,
        notification: HtmlNotification,
        sender: str | None = None,
        recipient: str | None = None,
    ) -> None:
        raise NotImplementedError()


class SmtpNotifier(Notifier):
    def __init__(
        self,
        smtp_client: aiosmtplib.SMTP,
        sender: str | None = None,
        recipient: str | None = None,
    ):
        self._client = smtp_client
        self._sender = sender or ""
        self._recipient = recipient or ""
        self._lock = asyncio.Lock()

    async def send(
        self,
        notification: Notification,
        sender: str | None = None,
        recipient: str | None = None,
        attachment: Attachment | None = None,
    ) -> None:
        self._validate_sender_and_recipient(sender, recipient)

        email = message.EmailMessage()
        email["From"] = sender or self._sender
        email["To"] = recipient or self._recipient
        email["Subject"] = notification.subject
        email.set_content(notification.body)

        if attachment:
            email.add_attachment(
                attachment.payload.encode("utf-8"),
                maintype=attachment.main_type,
                subtype=attachment.sub_type,
                filename=attachment.file_name,
            )

        async with self._lock, self._client:
            try:
                await self._client.send_message(email)
            except (
                ValueError,
                aiosmtplib.SMTPResponseException,
                aiosmtplib.SMTPRecipientsRefused,
            ) as error:
                raise NotificationError("Error sending notification") from error

    async def send_html(
        self,
        notification: HtmlNotification,
        sender: str | None = None,
        recipient: str | None = None,
    ) -> None:
        self._validate_sender_and_recipient(sender, recipient)

        email = multipart.MIMEMultipart("alternative")
        email["From"] = sender or self._sender
        email["To"] = recipient or self._recipient
        email["Subject"] = notification.subject
        email.attach(text.MIMEText(await notification.body, "html", "utf-8"))

        async with self._lock, self._client:
            try:
                await self._client.send_message(email)
            except (
                ValueError,
                aiosmtplib.SMTPResponseException,
                aiosmtplib.SMTPRecipientsRefused,
            ) as error:
                raise NotificationError("Error sending HTML notification") from error

    def _validate_sender_and_recipient(
        self,
        sender: str | None = None,
        recipient: str | None = None,
    ) -> None:
        if not sender and not self._sender:
            raise ValueError("A sender must be specified!")

        if not recipient and not self._recipient:
            raise ValueError("A recipient must be specified!")
