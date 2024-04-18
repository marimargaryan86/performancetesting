from typing import TypeVar

import pydantic
import unidecode
from motor import motor_asyncio

from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_database(
    app: application.Application[_Settings],
    dsn: pydantic.MongoDsn,
    database_suffix: str | None = None,
) -> motor_asyncio.AsyncIOMotorDatabase:
    client = motor_asyncio.AsyncIOMotorClient(host=str(dsn), tz_aware=True)
    database_name = app.name

    if database_suffix:
        database_name = "{name}_{suffix}".format(
            name=database_name,
            suffix=unidecode.unidecode(database_suffix),
        )

    return client[database_name.replace("-", "_")]
