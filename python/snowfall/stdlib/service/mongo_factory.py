import pydantic
from motor import motor_asyncio

from snowfall.stdlib.service import application


async def make_database(
    app: application.AsyncApplication[application.Settings],
    dsn: pydantic.MongoDsn,
) -> motor_asyncio.AsyncIOMotorDatabase:
    client = motor_asyncio.AsyncIOMotorClient(host=str(dsn))

    return client[app.name]
