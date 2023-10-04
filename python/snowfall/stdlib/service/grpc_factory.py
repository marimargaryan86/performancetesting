from typing import TypeVar

from grpc import aio

from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import client

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_insecure_channel(
    app: application.Application[_Settings],
    target: str,
) -> aio.Channel:
    channel = client.create_channel(target)

    return await app.stack.enter_async_context(channel)
