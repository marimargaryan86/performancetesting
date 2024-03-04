import dataclasses
from email import message

import aiosmtplib


@dataclasses.dataclass(frozen=True)
class Attachment(object):
    payload: str | bytes
    main_type: str
    sub_type: str
    file_name: str


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP, client_name: str, support_email: str):
        self._smtp = client
        self.client_name = client_name
        self.support_email = support_email

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
            payload = (
                attachment.payload.encode("utf-8")
                if isinstance(attachment.payload, str)
                else attachment.payload
            )
            email.add_attachment(
                payload,
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
        attachments: list[Attachment] | None = None,
    ) -> None:
        email = message.EmailMessage()
        email["From"] = "no-reply@snowfalltravel.com"
        email["To"] = mail_to
        email["Subject"] = subject

        email.set_content(body, subtype="html")

        if attachments:
            for attachment in attachments:
                email.add_attachment(
                    attachment.payload,
                    maintype=attachment.main_type,
                    subtype=attachment.sub_type,
                    filename=attachment.file_name,
                )

        async with self._smtp:
            await self._smtp.send_message(email)
