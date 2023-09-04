from typing import TypeVar

import pydantic
from motor import core, motor_asyncio

from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_database(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.MongoDsn,
) -> core.AgnosticDatabase:
    client = motor_asyncio.AsyncIOMotorClient(host=str(dsn))

    return client[app.name]
