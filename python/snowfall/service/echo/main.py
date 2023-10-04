import ipaddress
from collections.abc import Sequence

import pydantic
from grpc import aio

from snowfall.service.echo.v1 import echo_pb2, echo_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _AmqpSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: application.NetworkPort = 50051


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


async def _grpc(app: application.Application[_GrpcSettings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [_EchoService()],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


async def _produce(app: application.Application[_AmqpSettings]) -> None:
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    echo_producer = producer.Producer(
        connection=connection,
        exchange=types.Exchange(app.name),
    )

    await echo_producer.publish(
        echo_pb2.EchoRequest(echo="foobar"),
        "echo.foobar",
    )


class _Queue(consumer.AbstractQueue[echo_pb2.EchoRequest]):
    def __init__(self, name: str):
        self._logger = stdout.get_logger()
        self._name = name

    @property
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        return [
            (types.Exchange(self._name), "echo.foobar"),
        ]

    @property
    def name(self) -> str:
        return "{0}_consumer".format(self._name)

    async def on_message(self, msg: types.Message[echo_pb2.EchoRequest]) -> None:
        self._logger.info(msg.body.echo)


async def _consume(app: application.Application[_AmqpSettings]) -> None:
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    await consumer.QueueConsumer(connection, [_Queue(name=app.name)]).consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="echo")

    entrypoint.enter_with_commands(
        application.Command(
            name="consume",
            callback=_consume,
            settings_class=_AmqpSettings,
        ),
        application.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
        application.Command(
            name="produce",
            callback=_produce,
            settings_class=_AmqpSettings,
        ),
    )
