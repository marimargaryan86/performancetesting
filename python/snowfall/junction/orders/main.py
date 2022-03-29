import datetime
import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.junction.orders import orders
from snowfall.junction.orders.grpc import OrderService
from snowfall.stdlib import service
from snowfall.stdlib.transport import grpc


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50057
    mongo_dsn: Sequence[pydantic.AnyUrl]
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    grpc_server = grpc.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            OrderService(
                orders_searches=orders.OrderRepository(
                    mongo.orders.order_searches,
                    app.settings.default_ttl,
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
