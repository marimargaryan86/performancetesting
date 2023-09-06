from __future__ import annotations

from typing import AnyStr, Literal, TypeVar, overload

import pydantic
from redis import asyncio as aioredis

from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.service import application

_Settings = TypeVar("_Settings", bound=application.Settings)


@overload
async def make_client(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[False],
) -> types.Client[bytes]:
    """Deals with bytes when decode_responses=False."""


@overload
async def make_client(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True],
) -> types.Client[str]:
    """Deals with strings when decode_responses=True."""


async def make_client(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True, False],
) -> types.Client[AnyStr]:
    return types.Client(
        redis=await make_connection(
            app=app,
            dsn=dsn,
            decode_responses=decode_responses,
        ),
        prefix=app.name,
    )


@overload
async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[False],
) -> aioredis.Redis[bytes]:
    """Deals with bytes when decode_responses=False."""


@overload
async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True],
) -> aioredis.Redis[str]:
    """Deals with strings when decode_responses=True."""


@overload
async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: Literal[True, False],
) -> aioredis.Redis[AnyStr]:
    """Fallback for when a literal is passed."""


async def make_connection(
    app: application.AsyncApplication[_Settings],
    dsn: pydantic.RedisDsn,
    *,
    decode_responses: bool,
) -> aioredis.Redis[AnyStr]:
    return await app.stack.enter_async_context(
        aioredis.from_url(
            url=str(dsn),
            decode_responses=decode_responses,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
