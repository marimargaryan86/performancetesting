import datetime
import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.junction.orders import orders
from snowfall.junction.orders.grpc import OrderService
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import grpc


class _GrpcSettings(pydantic.BaseSettings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50057
    mongo_dsn: Sequence[pydantic.AnyUrl]
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    server = grpc.create_server(
        settings.grpc_address,
        settings.grpc_port,
        [
            OrderService(
                orders_searches=orders.OrderRepository(
                    mongo.orders.order_searches,
                    settings.default_ttl,
                ),
                default_page_size=settings.default_page_size,
            ),
        ],
    )

    await server.start()
    service.add_cleanup_task(server.stop(5))
    await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="orders",
        tasks=(Task(command="grpc", method=_serve),),
        # todo: add import task
    )

    _service.run()
