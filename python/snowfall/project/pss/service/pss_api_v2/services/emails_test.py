from email import message
from typing import cast
from unittest.mock import MagicMock, create_autospec

import aiosmtplib
from pydantic.networks import AnyUrl, EmailStr

from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService
from snowfall.project.pss.service.pss_api_v2.settings import Settings


async def test_that_send_forgotten_password_email_invokes_client() -> None:
    settings = Settings(
        mysql_dsn=cast(AnyUrl, "https://test-msql.com"),
        pss_v1_dsn=cast(AnyUrl, "https://test-pss.com"),
        smtp_dsn=cast(AnyUrl, "https://test-smtp.com"),
        smtp_sender=cast(EmailStr, "test@sender.com"),
        web_dsn=cast(AnyUrl, "https://test-website.com"),
    )
    client_mock: MagicMock = create_autospec(
        aiosmtplib.SMTP,
        spec_set=True,
        instance=True,
    )

    emails_service = SMTPEmailService(client_mock, settings)
    await emails_service.send_forgotten_password_email(  # nosec
        token="test-token",
        recipient="test-recipient",
    )

    client_mock.send_message.assert_called_once()
    sent_email: message.EmailMessage = client_mock.send_message.mock_calls[0][1][0]
    assert sent_email["From"] == "test@sender.com"
    assert sent_email["To"] == "test-recipient"
    assert sent_email["Subject"] == "Split Express - password reset"
    body = sent_email.get_body()
    assert body
    assert "test-token" in body.as_string()
