from typing import TypeVar

from grpc import aio

from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import metrics, tracing

_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_insecure_channel(
    app: application.Application[_Settings],
    target: str,
) -> aio.Channel:
    channel = aio.insecure_channel(
        target,
        interceptors=[
            tracing.TracingClientInterceptor(),
            metrics.MetricsClientInterceptor(),
        ],
    )

    return await app.stack.enter_async_context(channel)
