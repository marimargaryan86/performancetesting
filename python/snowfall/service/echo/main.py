import ipaddress

from grpc import aio

from snowfall.service.echo.v1 import echo_pb2, echo_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _EchoService(grpc_service.Service, echo_pb2_grpc.EchoServiceServicer):
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


async def _serve(app: service.Application[_Settings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [_EchoService()],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="echo")

    entrypoint.enter_with_commands(
        service.Command(name="grpc", callback=_serve, settings_class=_Settings),
    )
