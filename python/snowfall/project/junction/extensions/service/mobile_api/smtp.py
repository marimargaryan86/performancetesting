import dataclasses
from email import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from snowfall.stdlib.logging import stdout


@dataclasses.dataclass(frozen=True)
class Attachment(object):
    payload: str
    main_type: str
    sub_type: str
    file_name: str


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP, client_name: str, support_email: str):
        self._smtp = client
        self.client_name = client_name
        self.support_email = support_email
        self._logger = stdout.get_logger()

    async def send_email_notification(
        self,
        mail_to: str,
        subject: str,
        body: str,
        attachment: Attachment | None,
    ) -> None:
        email = message.EmailMessage()
        email["From"] = "no-reply@snowfalltravel.com"
        email["To"] = mail_to
        email["Subject"] = subject
        email.set_content(body)

        if attachment:
            email.add_attachment(
                attachment.payload.encode("utf-8"),
                maintype=attachment.main_type,
                subtype=attachment.sub_type,
                filename=attachment.file_name,
            )

        async with self._smtp:
            await self._smtp.send_message(email)

    async def send_email_html_template(
        self,
        mail_to: str,
        subject: str,
        body: str,
    ) -> None:
        email = MIMEMultipart("alternative")
        email["From"] = "no-reply@snowfalltravel.com"
        email["To"] = mail_to
        email["Subject"] = subject
        email.attach(MIMEText(body, "html", "utf-8"))

        async with self._smtp:
            send_message_resp = await self._smtp.send_message(email)
            self._logger.info(
                "Got response for sending message",
                response=send_message_resp,
            )
