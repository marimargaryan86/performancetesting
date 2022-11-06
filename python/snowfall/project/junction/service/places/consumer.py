from snowfall.project.junction.service.places.places import LocationRepository
from snowfall.project.junction.service.places.v1alpha.models_pb2 import Location
from snowfall.stdlib.transport.amqp.consumer import Consumer
from snowfall.stdlib.transport.amqp.types import Message


class LocationImportConsumer(object):
    def __init__(self, locations: LocationRepository, consumer: Consumer[Location]):
        self._consumer = consumer
        self._locations = locations

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message[Location]) -> None:
        if await self._locations.upsert(message.body):
            await message.ack()
        else:
            await message.nack()
