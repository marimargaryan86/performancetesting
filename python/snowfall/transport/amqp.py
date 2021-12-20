from typing import List, Type, Union

import kombu
from google.protobuf import symbol_database
from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message as ProtobufMessage
from kombu.mixins import ConsumerMixin
from kombu.serialization import register
from kombu.transport.base import StdChannel


class Serializer(object):
    """Protobuf Serializer."""

    _db = symbol_database.Default()

    @classmethod
    def serialize(cls, message: ProtobufMessage) -> bytes:
        """Serialize a message."""
        any_message = Any()

        any_message.Pack(message)

        return any_message.SerializeToString()

    @classmethod
    def deserialize(cls, blob: Union[bytes, memoryview]) -> ProtobufMessage:
        """Deserialize a message."""
        packed_message = Any()

        if isinstance(blob, memoryview):
            blob = blob.tobytes()

        packed_message.ParseFromString(blob)

        symbol: Type[ProtobufMessage] = cls._db.GetSymbol(
            packed_message.TypeName(),
        )
        unpacked_message = symbol()

        packed_message.Unpack(unpacked_message)

        return unpacked_message


register(
    name="protobuf",
    encoder=Serializer.serialize,
    decoder=Serializer.deserialize,
    content_type="application/x-protobuf",
    content_encoding="binary",
)


class Producer(kombu.Producer):
    """Message Fanout Producer.

    Publishes protobuf messages to an exchange identified by `exchange_name` argument
    over connection set by `connection_string` argument.

    Example:
        .. code-block:: python

            producer = Producer("amqp://localhost:5672/", "tasks")
            task = Task(arg1=value1, arg2=value2)
            producer.publish(task)
    """

    def __init__(self, connection_string: str, exchange_name: str):
        connection = kombu.Connection(connection_string)
        exchange = kombu.Exchange(exchange_name, "fanout")
        super().__init__(connection, exchange=exchange, serializer="protobuf")


class Consumer(ConsumerMixin):
    """Base class for consuming messages in "fanout" mode.

    Consumes protobuf messages from an exchange identified by `exchange_name` argument
    using a queue identified by `queue_name` argument over connection set by
    `connection_string` argument. This class should be extended in order to implement
    `process_message` method.

    Example:
        .. code-block:: python

            class ConcreteConsumer(Consumer):

                def process_message(
                    self,
                    body: google.protobuf.message.Message,
                    message: kombu.Message
                ):
                    print('Got task: {0!r}'.format(body))
                    message.ack()

            consumer = ConcreteConsumer("amqp://localhost:5672/", "tasks", "tasks_queue")
            consumer.run()
    """

    def __init__(
        self,
        connection_string: str,
        exchange_name: str,
        queue_name: str,
    ):
        self.connection = kombu.Connection(connection_string)
        self._exchange_name = exchange_name
        self._queue_name = queue_name

    def process_message(self, body: ProtobufMessage, message: kombu.Message) -> None:
        raise NotImplementedError

    def get_consumers(
        self,
        consumer: Type[kombu.Consumer],
        channel: StdChannel,
    ) -> List[kombu.Consumer]:
        queue = kombu.Queue(
            self._queue_name,
            exchange=kombu.Exchange(self._exchange_name, "fanout"),
        )
        return [
            consumer(
                queues=[queue],
                callbacks=[self.process_message],
                no_ack=True,
                accept=["protobuf"],
            ),
        ]
