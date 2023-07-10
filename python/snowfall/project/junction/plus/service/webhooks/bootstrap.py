import lagom

from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    flight_stats_app_key: str


def create_dependencies() -> lagom.Container:
    return lagom.Container()
