from pydantic import AnyUrl, BaseSettings, EmailStr

from snowfall.stdlib.integration.starlette import application


class Settings(BaseSettings, application.Settings):
    mysql_dsn: AnyUrl
    pss_v1_dsn: AnyUrl
    smtp_dsn: AnyUrl
    smtp_sender: EmailStr
    smtp_starttls: bool = True
    web_dsn: AnyUrl

    class Config(application.Settings.Config):
        """Inherits the Config from application.Settings to keep MyPy happy."""


def get_settings() -> Settings:
    return Settings()
