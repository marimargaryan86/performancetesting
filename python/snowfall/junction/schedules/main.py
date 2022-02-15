import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings

from snowfall.junction.schedules.consumer import ScheduleImportConsumer
from snowfall.junction.schedules.schedules import ScheduleRepository
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp


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


if __name__ == "__main__":
    _service = make_runnable_service(
        name="schedules",
        tasks=(Task(command="import", method=_import),),
    )

    _service.run()
