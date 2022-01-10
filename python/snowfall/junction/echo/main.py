import asyncio

from grpc import aio
from pydantic import BaseSettings

from snowfall.junction.echo.v1 import echo_pb2, echo_pb2_grpc
from snowfall.transport.grpc import Service, create_server


class Settings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051


class EchoService(Service, echo_pb2_grpc.EchoServiceServicer):
    def get_name(self) -> str:
        return echo_pb2.DESCRIPTOR.services_by_name["EchoService"].full_name

    def register(self, server: aio.Server) -> None:
        echo_pb2_grpc.add_EchoServiceServicer_to_server(self, server)

    async def Echo(  # type: ignore[override] # noqa: N802
        self,
        request: echo_pb2.EchoRequest,
        context: aio.ServicerContext,
    ) -> echo_pb2.EchoResponse:
        return echo_pb2.EchoResponse(
            echo=request.echo,
        )


async def serve() -> None:
    settings = Settings()
    server = create_server(
        settings.grpc_address,
        settings.grpc_port,
        [EchoService()],
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
