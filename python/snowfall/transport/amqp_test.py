import pytest
from google.protobuf.message import Message as ProtobufMessage
from google.protobuf.timestamp_pb2 import Timestamp
from kombu import Message

from snowfall.transport.amqp import Consumer, Producer, Serializer

seconds = 1639696695


class _TestConsumer(Consumer):
    def _process_message(self, body: ProtobufMessage, message: Message) -> None:
        """Do nothing for now."""


@pytest.mark.asyncio
async def test_publish_consume_async() -> None:
    producer = Producer.from_dsn("memory://", "foobar")
    consumer = _TestConsumer.from_dsn("memory://", "foobar", "foobar", "foobar")
    future = consumer.start()
    message = Timestamp(seconds=seconds)

    await producer.publish(message, "foobar")
    await consumer.stop()
    await future


class TestSerializer(object):
    def test_serialize(self) -> None:
        message = Timestamp(seconds=seconds)
        message_serialized = Serializer.serialize(message)
        assert isinstance(message_serialized, bytes)

    def test_deserialize(self) -> None:
        blob = (
            b"\n-type.googleapis.com/google.protobuf.Timestamp\x12\x06\x08\xb7\x92\xef"
            + b"\x8d\x06"
        )
        message = Serializer.deserialize(blob)
        assert isinstance(message, Timestamp)
        assert message.seconds == seconds
