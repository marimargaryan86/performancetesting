import datetime

import lagom

from snowfall.project.junction.plus.adapter import (
    subscribers,
)
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    notifications_address: str
    authentication_address: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)


def create_dependencies(
    subscribers_client: subscribers.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[subscribers.Client] = subscribers_client  # type: ignore[type-abstract]
    return container
