import asyncio
import ipaddress
import random
from typing import Sequence, cast

from grpc import aio
from pydantic import AnyUrl
from structlog import get_logger

from snowfall.service.echo.v1 import echo_pb2, echo_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _AmqpSettings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]


class _GrpcSettings(service.Settings):
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


async def _grpc(app: service.Application[_GrpcSettings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [_EchoService()],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


async def _produce(app: service.Application[_AmqpSettings]) -> None:
    connection = await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    )

    async with connection:
        producer = amqp.Producer(
            connection=connection,
            exchange=amqp.Exchange(app.name),
        )

        for _ in range(10):
            await producer.publish(echo_pb2.EchoRequest(echo="foobar"), "echo.foobar")


async def _echo_message_and_sleep(message: amqp.Message) -> None:
    echo_request = cast(echo_pb2.EchoRequest, message.body)

    get_logger(__name__).info(echo_request.echo)

    await asyncio.sleep(5)


async def _consume(app: service.Application[_AmqpSettings]) -> None:
    connection = await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    )

    async with connection:
        consumer = amqp.Consumer(
            connection=connection,
            exchange=amqp.Exchange(app.name),
            queue_name="{0}_consumer".format(app.name),
            routing_key="echo.foobar",
        )

        await consumer.consume(_echo_message_and_sleep)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="echo")

    entrypoint.enter_with_commands(
        service.Command(
            name="consume",
            callback=_consume,
            settings_class=_AmqpSettings,
        ),
        service.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
        service.Command(
            name="produce",
            callback=_produce,
            settings_class=_AmqpSettings,
        ),
    )
