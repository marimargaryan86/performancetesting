import ipaddress
from abc import abstractmethod
from typing import Sequence

from grpc import aio
from grpc_health.v1 import health, health_pb2_grpc
from grpc_reflection.v1alpha import reflection


class Service(object):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def register(self, server: aio.Server) -> None:
        raise NotImplementedError()


def create_server(
    address: ipaddress.IPv4Address,
    port: int,
    services: Sequence[Service],
) -> aio.Server:
    server = aio.server()
    names = {reflection.SERVICE_NAME}

    server.add_insecure_port("{address}:{port}".format(address=str(address), port=port))

    for service in (*services, _HealthService()):
        service.register(server)
        names.add(service.get_name())

    reflection.enable_server_reflection(list(names), server)

    return server


class _HealthService(Service):
    def get_name(self) -> str:
        return health.SERVICE_NAME

    def register(self, server: aio.Server) -> None:
        health_pb2_grpc.add_HealthServicer_to_server(
            health.aio.HealthServicer(),
            server,
        )
