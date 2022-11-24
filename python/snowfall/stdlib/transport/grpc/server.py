import asyncio
import ipaddress
from collections.abc import AsyncGenerator
from typing import Sequence

import asyncstdlib
import grpc
from grpc_reflection.v1alpha import reflection
from structlog import get_logger

from snowfall.stdlib.transport.grpc import handler, metrics, tracing
from snowfall.stdlib.transport.grpc.service import HealthService, Service


class Server(object):
    def __init__(self, server: grpc.aio.Server, address: str):
        self._address = address
        self._logger = get_logger(__name__)
        self._server = server

    @asyncstdlib.contextmanager
    async def serve(self) -> AsyncGenerator[grpc.aio.Server, None]:
        await self._server.start()
        self._logger.info("gRPC server started.", address=self._address)

        try:
            yield self._server
        except asyncio.CancelledError:
            await self._server.stop(5)


def create_server(
    address: ipaddress.IPv4Address,
    port: int,
    services: Sequence[Service],
) -> Server:
    server = grpc.aio.server(
        interceptors=[
            tracing.TracingServerInterceptor(),
            metrics.MetricsServerInterceptor(),
            handler.ErrorHandlerServerInterceptor(),
        ],
    )
    names = {reflection.SERVICE_NAME}
    address_concat = "{address}:{port}".format(address=str(address), port=port)

    server.add_insecure_port(address_concat)

    for service in (*services, HealthService()):
        service.register(server)
        names.add(service.get_name())

    reflection.enable_server_reflection(list(names), server)

    return Server(server, address_concat)
