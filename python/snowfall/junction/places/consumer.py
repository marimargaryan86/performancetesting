from typing import cast

from snowfall.common.v1alpha.models_pb2 import Place
from snowfall.junction.places.places import PlaceRepository
from snowfall.stdlib.transport.amqp import Consumer, Message


class PlaceImportConsumer(object):
    def __init__(self, places: PlaceRepository, consumer: Consumer):
        self._consumer = consumer
        self._places = places

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message) -> None:
        place = cast(Place, message.body)

        if await self._places.upsert(place):
            await message.ack()
        else:
            await message.nack()
