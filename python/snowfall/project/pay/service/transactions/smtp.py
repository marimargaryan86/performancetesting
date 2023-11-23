import dataclasses
from email import message

import aiosmtplib


@dataclasses.dataclass(frozen=True)
class Attachment(object):
    payload: str
    main_type: str
    sub_type: str
    file_name: str


class EmailClient(object):
    def __init__(
        self,
        client: aiosmtplib.SMTP,
        from_email: str,
        to_email: str,
    ):
        self._client = client
        self._from_email = from_email
        self._to_email = to_email

    async def send_email(
        self,
        subject: str,
        body: str,
        attachment: Attachment | None,
    ) -> None:
        email = message.EmailMessage()
        email["From"] = self._from_email
        email["To"] = self._to_email
        email["Subject"] = subject
        email.set_content(body)

        if attachment:
            email.add_attachment(
                attachment.payload.encode("utf-8"),
                maintype=attachment.main_type,
                subtype=attachment.sub_type,
                filename=attachment.file_name,
            )

        async with self._client:
            await self._client.send_message(email)
