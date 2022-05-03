from abc import abstractmethod

from grpc import aio
from grpc_health.v1 import health, health_pb2_grpc


class Service(object):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def register(self, server: aio.Server) -> None:
        raise NotImplementedError()


class HealthService(Service):
    def get_name(self) -> str:
        return health.SERVICE_NAME

    def register(self, server: aio.Server) -> None:
        health_pb2_grpc.add_HealthServicer_to_server(
            health.aio.HealthServicer(),
            server,
        )
