import pydantic
from motor import motor_asyncio

from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import types


async def make_connection(
    app: application.AsyncApplication[application.Settings],
    dsn: pydantic.AmqpDsn,
) -> motor_asyncio.AsyncIOMotorDatabase:
    return await app.stack.enter_async_context(
        types.Connection(str(dsn)),
    )
