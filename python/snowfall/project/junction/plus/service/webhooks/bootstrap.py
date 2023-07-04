import lagom

from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    secret_key: str


def create_dependencies() -> lagom.Container:
    return lagom.Container()
