from typing import TypeVar

import pydantic
from motor import motor_asyncio

from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import types

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.AmqpDsn,
) -> motor_asyncio.AsyncIOMotorDatabase:
    return await app.stack.enter_async_context(
        types.Connection(str(dsn)),
    )
