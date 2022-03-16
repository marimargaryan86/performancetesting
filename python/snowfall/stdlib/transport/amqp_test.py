from google.protobuf.timestamp_pb2 import Timestamp

from snowfall.stdlib.transport.amqp import Serializer

_seconds = 1639696695


class TestSerializer(object):
    def test_serialize(self) -> None:
        message = Timestamp(seconds=_seconds)
        message_serialized = Serializer.serialize(message)
        assert isinstance(message_serialized, bytes)

    def test_deserialize(self) -> None:
        blob = (
            b"\n-type.googleapis.com/google.protobuf.Timestamp\x12\x06\x08\xb7\x92\xef"
            + b"\x8d\x06"
        )
        message = Serializer.deserialize(blob)
        assert isinstance(message, Timestamp)
        assert message.seconds == _seconds
