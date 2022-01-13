from snowfall.transport.amqp import Consumer, Message


class PlaceImportConsumer(object):
    def __init__(self, consumer: Consumer):
        self._consumer = consumer

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: Message) -> None:
        await message.ack()
