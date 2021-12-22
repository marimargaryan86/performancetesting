from __future__ import annotations

import asyncio
import functools
from abc import ABC, abstractmethod
from concurrent import futures
from typing import List, Type, Union

from google.protobuf import any_pb2, symbol_database
from google.protobuf.message import Message as ProtobufMessage
from kombu import Connection
from kombu import Consumer as KombuConsumer
from kombu import Exchange, Message, Queue, connection, mixins, pools, serialization
from kombu.transport.base import StdChannel


class Serializer(object):
    _db = symbol_database.Default()

    @classmethod
    def serialize(cls, message: ProtobufMessage) -> bytes:
        any_message = any_pb2.Any()

        any_message.Pack(message)

        return any_message.SerializeToString()

    @classmethod
    def deserialize(cls, blob: Union[bytes, memoryview]) -> ProtobufMessage:
        packed_message = any_pb2.Any()

        if isinstance(blob, memoryview):
            blob = blob.tobytes()

        packed_message.ParseFromString(blob)

        symbol: Type[ProtobufMessage] = cls._db.GetSymbol(
            packed_message.TypeName(),
        )
        unpacked_message = symbol()

        packed_message.Unpack(unpacked_message)

        return unpacked_message


serialization.register(
    name="protobuf",
    encoder=Serializer.serialize,
    decoder=Serializer.deserialize,
    content_type="application/x-protobuf",
    content_encoding="binary",
)


class Producer(object):
    def __init__(self, pool: pools.ProducerPool, exchange: Exchange):
        self._exchange = exchange
        self._pool = pool

    @classmethod
    def from_dsn(cls, dsn: str, exchange_name: str) -> Producer:
        return cls(
            pool=pools.producers[Connection(dsn)],
            exchange=Exchange(exchange_name, type="topic"),
        )

    async def publish(self, message: ProtobufMessage, routing_key: str) -> None:
        loop = asyncio.get_running_loop()

        with futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                functools.partial(self._publish, message, routing_key),
            )

    def _publish(self, message: ProtobufMessage, routing_key: str) -> None:
        with self._pool.acquire(block=True) as producer:
            producer.publish(
                message,
                exchange=self._exchange,
                routing_key=routing_key,
                declare=[self._exchange],
                retry=True,
                serializer="protobuf",
            )


class Consumer(ABC, mixins.ConsumerMixin):
    def __init__(self, pool: connection.ConnectionPool, queue: Queue):
        self.connection = pool.acquire(block=True)
        self._queue = queue

    @classmethod
    def from_dsn(
        cls,
        dsn: str,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
    ) -> Consumer:
        return cls(
            pool=pools.connections[Connection(dsn)],
            queue=Queue(
                name=queue_name,
                exchange=Exchange(exchange_name, "topic"),
                routing_key=routing_key,
            ),
        )

    async def start(self) -> None:
        loop = asyncio.get_running_loop()

        with futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, self.run)

    async def stop(self) -> None:
        self.should_stop = True

    def get_consumers(
        self,
        consumer: Type[KombuConsumer],
        channel: StdChannel,
    ) -> List[KombuConsumer]:
        return [
            consumer(
                queues=[self._queue],
                callbacks=[self._handle_message],
                no_ack=False,
                accept=["protobuf"],
            ),
        ]

    def _handle_message(self, body: ProtobufMessage, message: Message) -> None:
        try:
            self._process_message(body, message)
        except Exception:  # noqa: PIE786
            # todo: log

            if not message.acknowledged:
                message.reject()
        else:
            if not message.acknowledged:
                message.ack()

    @abstractmethod
    def _process_message(self, body: ProtobufMessage, message: Message) -> None:
        raise NotImplementedError
