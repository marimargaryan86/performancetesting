import aiosmtplib
from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings


def get_smtp_client(settings: Settings = Depends(get_settings)) -> aiosmtplib.SMTP:
    return aiosmtplib.SMTP(
        hostname=settings.smtp_dsn.host,
        port=int(settings.smtp_dsn.port or 0) or None,
        username=settings.smtp_dsn.user,
        password=settings.smtp_dsn.password,
        start_tls=settings.smtp_starttls,
    )
