import asyncio
import types

from motor import motor_asyncio

from snowfall.stdlib import string


class TemporaryDatabase:
    def __init__(
        self,
        mongo: motor_asyncio.AsyncIOMotorClient,
        prefix: str = "",
    ) -> None:
        self._mongo = mongo
        self._db_name = "{prefix}_{random}".format(
            prefix=(prefix or "temp"),
            random=string.random(8),
        )

    async def __aenter__(self) -> motor_asyncio.AsyncIOMotorDatabase:
        return self._mongo[self._db_name]

    async def __aexit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: types.TracebackType | None,
    ) -> None:
        try:
            await self._mongo.drop_database(self._db_name)
        except asyncio.CancelledError:
            await self._mongo.drop_database(self._db_name)
