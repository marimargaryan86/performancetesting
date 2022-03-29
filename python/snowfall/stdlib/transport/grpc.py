import asyncio
import ipaddress
from abc import abstractmethod
from collections.abc import AsyncGenerator
from typing import Sequence

import asyncstdlib
from grpc import aio
from grpc_health.v1 import health, health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from structlog import get_logger


class Service(object):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def register(self, server: aio.Server) -> None:
        raise NotImplementedError()


class Server(object):
    def __init__(self, server: aio.Server, address: str):
        self._address = address
        self._logger = get_logger(__name__)
        self._server = server

    @asyncstdlib.contextmanager
    async def serve(self) -> AsyncGenerator[aio.Server, None]:
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
    server = aio.server()
    names = {reflection.SERVICE_NAME}
    address_concat = "{address}:{port}".format(address=str(address), port=port)

    server.add_insecure_port(address_concat)

    for service in (*services, _HealthService()):
        service.register(server)
        names.add(service.get_name())

    reflection.enable_server_reflection(list(names), server)

    return Server(server, address_concat)


class _HealthService(Service):
    def get_name(self) -> str:
        return health.SERVICE_NAME

    def register(self, server: aio.Server) -> None:
        health_pb2_grpc.add_HealthServicer_to_server(
            health.aio.HealthServicer(),
            server,
        )
