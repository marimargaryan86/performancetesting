"""Implementation of the Echo gRPC service."""
import asyncio

from grpc import aio
from grpc_health.v1 import health, health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from pydantic import BaseSettings

from snowfall.junction.echo.v1 import echo_pb2, echo_pb2_grpc


class Settings(BaseSettings):
    grpc_port: int = 50051

    class Config(object):  # noqa: WPS431
        case_sensitive = False
        fields = {
            "grpc_port": {
                "env": "NOMAD_PORT_GRPC",
            },
        }


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    def Echo(  # noqa: N802
        self,
        request: echo_pb2.EchoRequest,
        context: aio.ServicerContext,
    ) -> echo_pb2.EchoResponse:
        return echo_pb2.EchoResponse(
            echo=request.echo,
        )


async def serve() -> None:
    settings = Settings()
    server = aio.server()

    server.add_insecure_port("[::]:{port}".format(port=settings.grpc_port))
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    reflection.enable_server_reflection(
        [
            echo_pb2.DESCRIPTOR.services_by_name["EchoService"].full_name,
            health.SERVICE_NAME,
            reflection.SERVICE_NAME,
        ],
        server,
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
