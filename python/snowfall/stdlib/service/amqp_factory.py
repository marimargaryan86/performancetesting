import datetime
from typing import TypeVar

import pydantic
from aio_pika import abc, connect_robust

from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_connection(
    app: application.Application[_Settings],
    dsn: pydantic.AmqpDsn,
    timeout: datetime.timedelta | None = None,
) -> abc.AbstractConnection:
    return await app.stack.enter_async_context(
        await connect_robust(
            url=str(dsn),
            timeout=timeout.total_seconds() if timeout else None,
        ),
    )
