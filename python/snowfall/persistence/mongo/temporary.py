import contextlib
import random
import string
from typing import AsyncIterator

from motor import core


@contextlib.asynccontextmanager
async def database(
    mongo: core.AgnosticClient,
    prefix: str = "",
) -> AsyncIterator[core.AgnosticDatabase]:
    db_name = "{prefix}_{random}".format(
        prefix=(prefix or "temp"),
        random="".join(
            random.choices(string.ascii_uppercase + string.digits, k=8),  # nosec
        ),
    )

    try:
        yield mongo[db_name]
    finally:
        mongo.drop_database(db_name)
