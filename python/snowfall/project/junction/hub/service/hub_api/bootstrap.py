import lagom

from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    """Settings for hub-api."""


def create_dependencies() -> lagom.Container:
    # TODO: add dependencies here

    return lagom.Container()
