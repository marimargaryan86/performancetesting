from pydantic import BaseSettings

from snowfall.stdlib.integration.starlette import application


class Settings(BaseSettings, application.Settings):
    mysql_dsn: str
    pss_v1_dsn: str

    class Config(application.Settings.Config):
        """Inherits the Config from application.Settings to keep MyPy happy."""


def get_settings() -> Settings:
    return Settings()
