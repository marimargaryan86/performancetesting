"""Implementation of the Echo gRPC service."""
import asyncio

from grpc import aio
from grpc_reflection.v1alpha import reflection

from snowfall.junction.echo.v1 import echo_pb2, echo_pb2_grpc


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
    server = aio.server()

    server.add_insecure_port("[::]:50051")

    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    reflection.enable_server_reflection(
        [
            echo_pb2.DESCRIPTOR.services_by_name["EchoService"].full_name,
            reflection.SERVICE_NAME,
        ],
        server,
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
