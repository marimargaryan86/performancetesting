from typing import cast

from snowfall.project.junction.service.places.places import LocationRepository
from snowfall.project.junction.service.places.v1alpha.models_pb2 import Location
from snowfall.stdlib.transport.amqp import Consumer, Message


class LocationImportConsumer(object):
    def __init__(self, locations: LocationRepository, consumer: Consumer):
        self._consumer = consumer
        self._locations = locations

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message) -> None:
        place = cast(Location, message.body)

        if await self._locations.upsert(place):
            await message.ack()
        else:
            await message.nack()
