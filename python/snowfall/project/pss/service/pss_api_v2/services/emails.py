import copy
from email import message
from typing import Any

import aiofiles
import aiosmtplib
from fastapi import Depends
from jinja2 import Template

from snowfall.project.pss.service.pss_api_v2.clients.smtp import get_smtp_client
from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings
from snowfall.project.pss.service.pss_api_v2.translations.translations import (
    translations,
)
from snowfall.stdlib.persistence import filesystem

_TEMPLATES_PACKAGE_PATH = "snowfall.project.pss.service.pss_api_v2.templates"
_FORGOTTEN_PASSWORD_EMAIL_PATH = "forgot-password-email.html"  # nosec


class SMTPEmailError(Exception):
    """Raised when an exception occurred during sending."""


class SMTPEmailService(object):
    def __init__(
        self,
        client: aiosmtplib.SMTP = Depends(get_smtp_client),
        settings: Settings = Depends(get_settings),
    ) -> None:
        self._client = client
        self._settings = copy.deepcopy(settings)

    async def send_forgotten_password_email(
        self,
        token: str,
        recipient: str,
    ) -> None:
        async with aiofiles.open(
            filesystem.resource_path(
                _TEMPLATES_PACKAGE_PATH,
                _FORGOTTEN_PASSWORD_EMAIL_PATH,
            ),
        ) as template_file:
            template = Template(await template_file.read())
        template_args = {
            "web_url": self._settings.web_dsn,
            "translations": translations,
            "reset_password_url": "{0}en/reset-password/{1}".format(
                self._settings.web_dsn,
                token,
            ),
            "email_logo_url": "{0}assets/images/email-logo.png".format(
                self._settings.web_dsn,
            ),
        }
        body = self._render_template(
            Template(self._render_template(template, **template_args)),
            **template_args,
        )
        await self._send(
            email_content=body,
            recipient=recipient,
            subject=translations["forgot_password_subject"],
        )

    def _render_template(self, template: Template, **kwargs: Any) -> str:
        return template.render(kwargs)

    async def _send(self, email_content: str, recipient: str, subject: str) -> None:
        email = message.EmailMessage()
        email["From"] = self._settings.smtp_sender
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(email_content)
        email.set_type("text/html")

        async with self._client:
            try:
                await self._client.send_message(email)
            except (
                ValueError,
                aiosmtplib.SMTPResponseException,
                aiosmtplib.SMTPRecipientsRefused,
            ) as error:
                raise SMTPEmailError("Error when sending email") from error
