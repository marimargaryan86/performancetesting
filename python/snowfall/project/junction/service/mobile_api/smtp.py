from email import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP):
        self._smtp = client

    async def send_email_notification(
        self,
        mail_to: str,
        subject: str,
        body: str,
    ) -> None:
        email = message.EmailMessage()
        email["From"] = "no-reply@snowfalltravel.com"
        email["To"] = mail_to
        email["Subject"] = subject
        email.set_content(body)

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
            await self._smtp.send_message(email)
