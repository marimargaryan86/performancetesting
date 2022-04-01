import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.junction.orders import orders
from snowfall.junction.orders.amqp import OrderProducer
from snowfall.junction.orders.grpc import OrderService
from snowfall.stdlib import service
from snowfall.stdlib.transport import amqp, grpc


class _GrpcSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50057
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with amqp.Connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        grpc_server = grpc.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                OrderService(
                    orders=orders.OrderRepository(
                        mongo.orders.order,
                    ),
                    publisher=OrderProducer(
                        producer=await amqp.create_producer(
                            conn=connection,
                            exchange_name="orders",
                        ),
                    ),
                    default_page_size=app.settings.default_page_size,
                ),
            ],
        )

        async with grpc_server.serve() as server:
            await server.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="orders")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        # todo: add import task
    )
