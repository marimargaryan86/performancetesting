from typing import cast

from snowfall.project.junction.service.schedules.schedules import ScheduleRepository
from snowfall.stdlib.transport.amqp import Consumer, Message
from snowfall.stdlib.v1alpha.models_pb2 import Schedule


class ScheduleImportConsumer(object):
    def __init__(self, schedules: ScheduleRepository, consumer: Consumer):
        self._consumer = consumer
        self._schedules = schedules

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message) -> None:
        schedule = cast(Schedule, message.body)

        if await self._schedules.upsert(schedule):
            await message.ack()
        else:
            await message.nack()
