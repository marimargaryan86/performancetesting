from grpc import aio

from snowfall.stdlib.transport.grpc.tracing import TracingClientInterceptor


def create_channel(target: str) -> aio.Channel:
    return aio.insecure_channel(
        target,
        interceptors=[
            TracingClientInterceptor(),
        ],
    )
