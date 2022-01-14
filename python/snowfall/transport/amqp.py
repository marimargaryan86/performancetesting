from __future__ import annotations

import functools
from asyncio import Event
from typing import Callable, Coroutine, Type, Union, cast

from aiormq import abc
from google.protobuf import any_pb2, symbol_database
from google.protobuf.message import Message as ProtobufMessage
from pamqp import commands


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


class Producer(object):
    def __init__(
        self,
        channel: abc.AbstractChannel,
        exchange_name: str,
    ):
        self._channel = channel
        self._exchange_name = exchange_name

    async def publish(self, message: ProtobufMessage, routing_key: str) -> None:
        await self._channel.basic_publish(
            body=Serializer.serialize(message),
            exchange=self._exchange_name,
            routing_key=routing_key,
        )


async def create_producer(
    connection: abc.AbstractConnection,
    exchange_name: str,
    exchange_type: str = "topic",
) -> Producer:
    channel = await connection.channel()

    await channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=True,
    )

    return Producer(channel, exchange_name)


class Message(object):
    def __init__(self, message: abc.DeliveredMessage):
        self._acknowledged = False
        self._message = message

    async def ack(self) -> None:
        if self._acknowledged:
            raise RuntimeError("message already acknowledged")

        delivery = cast(commands.Basic.Deliver, self._message.delivery)

        await self._message.channel.basic_ack(cast(int, delivery.delivery_tag))

        self._acknowledged = True

    @property
    def acknowledged(self) -> bool:
        return self._acknowledged

    @property
    def body(self) -> ProtobufMessage:
        return Serializer.deserialize(self._message.body)

    async def nack(self) -> None:
        if self._acknowledged:
            raise RuntimeError("message already acknowledged")

        delivery = cast(commands.Basic.Deliver, self._message.delivery)

        await self._message.channel.basic_nack(cast(int, delivery.delivery_tag))

        self._acknowledged = True


ConsumerCallback = Callable[[Message], Coroutine[None, None, None]]


class Consumer(object):
    def __init__(
        self,
        channel: abc.AbstractChannel,
        queue_name: str,
    ):
        self._channel = channel
        self._queue_name = queue_name

    async def consume(self, callback: ConsumerCallback) -> None:
        await self._channel.basic_consume(
            self._queue_name,
            self._decorate_callback(callback),
        )

        # basic_consume() doesn't block while it consumes
        await Event().wait()

    @classmethod
    def _decorate_callback(
        cls,
        callback: ConsumerCallback,
    ) -> abc.ConsumerCallback:
        @functools.wraps(callback)
        async def decorator(message: abc.DeliveredMessage) -> None:
            msg = Message(message)

            try:
                await callback(msg)
            except Exception:  # noqa: PIE786
                # todo: log

                if not msg.acknowledged:
                    await msg.nack()
            else:
                if not msg.acknowledged:
                    await msg.ack()

        return decorator


async def create_consumer(
    connection: abc.AbstractConnection,
    exchange_name: str,
    queue_name: str,
    routing_key: str,
    exchange_type: str = "topic",
) -> Consumer:
    channel = await connection.channel()

    await channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=True,
    )

    await channel.queue_declare(
        queue=queue_name,
        durable=True,
    )

    await channel.queue_bind(
        queue=queue_name,
        exchange=exchange_name,
        routing_key=routing_key,
    )

    return Consumer(channel, queue_name)
