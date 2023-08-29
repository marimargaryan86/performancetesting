from __future__ import annotations

from typing import AnyStr, Literal, TypeVar, overload

import pydantic
from redis import asyncio as aioredis

from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)


@overload
async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[False],
) -> aioredis.Redis[bytes]:
    """Clients with decode_responses=False deals with bytes."""


@overload
async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True],
) -> aioredis.Redis[str]:
    """Clients with decode_responses=True deals with strings."""


async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True, False],
) -> aioredis.Redis[AnyStr]:
    return await app.stack.enter_async_context(
        aioredis.from_url(
            url=str(dsn),
            decode_responses=decode_responses,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
