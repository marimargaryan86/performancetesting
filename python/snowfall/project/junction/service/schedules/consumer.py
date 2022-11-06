from snowfall.project.junction.service.schedules.schedules import ScheduleRepository
from snowfall.stdlib.transport.amqp.consumer import Consumer
from snowfall.stdlib.transport.amqp.types import Message
from snowfall.stdlib.v1alpha.models_pb2 import Schedule


class ScheduleImportConsumer(object):
    def __init__(self, schedules: ScheduleRepository, consumer: Consumer[Schedule]):
        self._consumer = consumer
        self._schedules = schedules

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message[Schedule]) -> None:
        if await self._schedules.upsert(message.body):
            await message.ack()
        else:
            await message.nack()
