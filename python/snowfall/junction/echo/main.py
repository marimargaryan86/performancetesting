from grpc import aio
from pydantic import BaseSettings

from snowfall.junction.echo.v1 import echo_pb2, echo_pb2_grpc
from snowfall.service import Service, Task, make_service
from snowfall.transport import grpc


class _Settings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051


class _EchoService(grpc.Service, echo_pb2_grpc.EchoServiceServicer):
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


async def _serve(service: Service) -> None:
    settings = _Settings()
    server = grpc.create_server(
        settings.grpc_address,
        settings.grpc_port,
        [_EchoService()],
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_service(name="echo", tasks=(Task(command="grpc", method=_serve),))
    _service.run()
