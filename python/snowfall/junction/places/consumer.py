import kombu
from google.protobuf.message import Message as ProtobufMessage

from snowfall.transport.amqp import Consumer


class PlaceImportConsumer(Consumer):
    def _process_message(self, body: ProtobufMessage, message: kombu.Message) -> None:
        message.ack()
