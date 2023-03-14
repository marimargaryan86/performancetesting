import asyncio
import random
import string
import types

from motor import core


class TemporaryDatabase(object):
    def __init__(
        self,
        mongo: core.AgnosticClient,
        prefix: str = "",
    ) -> None:
        self._mongo = mongo
        self._db_name = "{prefix}_{random}".format(
            prefix=(prefix or "temp"),
            random="".join(
                random.choices(string.ascii_uppercase + string.digits, k=8),  # nosec
            ),
        )

    async def __aenter__(self) -> core.AgnosticDatabase:
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
