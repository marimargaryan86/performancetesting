from email import message

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
