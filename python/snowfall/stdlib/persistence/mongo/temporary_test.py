import pytest
from motor import motor_asyncio

from snowfall.stdlib.persistence.mongo import temporary


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "foobar",
    ],
)
async def test_temporary_database_is_temporary(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
    prefix: str,
) -> None:
    name: str

    async with temporary.TemporaryDatabase(mongo_client, prefix=prefix) as db:
        name = db.name

        # DBs are created lazily, so need to insert some data for it to exist.
        await db["foobar"].insert_one({"_id": "foobar"})

        assert name in await mongo_client.list_database_names()

    assert name not in await mongo_client.list_database_names()
