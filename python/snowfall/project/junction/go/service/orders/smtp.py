from email.mime import multipart, text

import aiosmtplib


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP):
        self._smtp = client

    async def send_email_html_template(
        self,
        mail_to: str,
        subject: str,
        body: str,
    ) -> None:
        email = multipart.MIMEMultipart("alternative")
        email["From"] = "no-reply@snowfalltravel.com"
        email["To"] = mail_to
        email["Subject"] = subject
        email.attach(text.MIMEText(body, "html", "utf-8"))

        async with self._smtp:
            await self._smtp.send_message(email)
