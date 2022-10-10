from email import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib


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
