import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings

from snowfall.junction.schedules.consumer import ScheduleImportConsumer
from snowfall.junction.schedules.grpc import ScheduleService
from snowfall.junction.schedules.schedules import ScheduleRepository
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp, grpc


class _GrpcSettings(BaseSettings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


class _ImportSettings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    mongo_dsn: Sequence[AnyUrl]


async def _import(service: RunnableService) -> None:
    settings = _ImportSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec

    async with connection:
        consumer = ScheduleImportConsumer(
            schedules=ScheduleRepository(mongo.schedules.schedules),
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="schedules",
                queue_name="{0}_schedules_importer".format(service.name),
                routing_key="schedule.import",
            ),
        )

        await consumer.consume()


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    server = grpc.create_server(
        settings.grpc_address,
        settings.grpc_port,
        [
            ScheduleService(
                schedules=ScheduleRepository(mongo.schedules.schedules),
                default_page_size=settings.default_page_size,
            ),
        ],
    )

    await server.start()
    service.add_cleanup_task(server.stop(5))
    await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="schedules",
        tasks=(
            Task(command="import", method=_import),
            Task(command="grpc", method=_serve),
        ),
    )

    _service.run()
