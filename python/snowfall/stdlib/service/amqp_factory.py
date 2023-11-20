import datetime
import logging
from collections.abc import Sequence
from typing import TypeVar

import pydantic
from aio_pika import abc, connect_robust

from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)

CONNECTION_FORCED = 320


class SkipConnectionLostFilter(logging.Filter):
    """Filter to skip connection lost error logs.

    Connection lost errors happen normally (e.g. when restarting the message
    queue). As we use connect_robust(), it will just reconnect, so we can ignore
    these.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            not isinstance(record.args, Sequence)
            or len(record.args) < 2
            or record.args[1] != CONNECTION_FORCED
        )


async def make_connection(
    app: application.Application[_Settings],
    dsn: pydantic.AmqpDsn,
    timeout: datetime.timedelta | None = None,
) -> abc.AbstractConnection:
    logging.getLogger("aiormq.connection").addFilter(SkipConnectionLostFilter())
    return await app.stack.enter_async_context(
        await connect_robust(
            url=str(dsn),
            timeout=timeout.total_seconds() if timeout else None,
        ),
    )
