import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from snowfall.transport.amqp import Serializer

seconds = 1639696695


@pytest.fixture
def serializer() -> Serializer:
    return Serializer()


class TestSerializer(object):
    def test_serialize(self, serializer: Serializer) -> None:
        message = Timestamp(seconds=seconds)
        message_serialized = serializer.serialize(message)
        assert isinstance(message_serialized, bytes)

    def test_deserialize(self, serializer: Serializer) -> None:
        blob = (
            b"\n-type.googleapis.com/google.protobuf.Timestamp\x12\x06\x08\xb7\x92\xef"
            + b"\x8d\x06"
        )
        message = serializer.deserialize(blob)
        assert isinstance(message, Timestamp)
        assert message.seconds == seconds
