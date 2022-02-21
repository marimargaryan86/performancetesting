from __future__ import annotations

import functools
from asyncio import Event
from types import TracebackType
from typing import Callable, Coroutine, Optional, Type, Union, cast

from aiormq import abc, connection
from google.protobuf import any_pb2, message, symbol_database
from pamqp import commands
from structlog import get_logger


class Serializer(object):
    _db = symbol_database.Default()

    @classmethod
    def serialize(cls, msg: message.Message) -> bytes:
        any_message = any_pb2.Any()

        any_message.Pack(msg)

        return any_message.SerializeToString()

    @classmethod
    def deserialize(cls, blob: Union[bytes, memoryview]) -> message.Message:
        packed_message = any_pb2.Any()

        if isinstance(blob, memoryview):
            blob = blob.tobytes()

        packed_message.ParseFromString(blob)

        symbol: Type[message.Message] = cls._db.GetSymbol(
            packed_message.TypeName(),
        )
        unpacked_message = symbol()

        packed_message.Unpack(unpacked_message)

        return unpacked_message


class Connection(connection.Connection):
    async def __aenter__(self) -> "Connection":
        await super().__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        await self.close(exc_val)
        return False


class Producer(object):
    def __init__(
        self,
        channel: abc.AbstractChannel,
        exchange_name: str,
    ):
        self._channel = channel
        self._exchange_name = exchange_name
        self._logger = get_logger(__name__)

    async def publish(self, msg: message.Message, routing_key: str) -> None:
        await self._channel.basic_publish(
            body=Serializer.serialize(msg),
            exchange=self._exchange_name,
            routing_key=routing_key,
        )

        self._logger.info(
            "Message published.",
            exchange=self._exchange_name,
            routing_key=routing_key,
            type=msg.DESCRIPTOR.full_name,
        )


async def create_producer(
    conn: Connection,
    exchange_name: str,
    exchange_type: str = "topic",
) -> Producer:
    channel = await conn.channel()

    await channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=True,
    )

    return Producer(channel, exchange_name)


class Message(object):
    def __init__(self, msg: abc.DeliveredMessage):
        self._acknowledged = False
        self._body = Serializer.deserialize(msg.body)
        self._message = msg

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
    def body(self) -> message.Message:
        return self._body

    async def nack(self) -> None:
        if self._acknowledged:
            raise RuntimeError("message already acknowledged")

        delivery = cast(commands.Basic.Deliver, self._message.delivery)

        await self._message.channel.basic_nack(
            cast(int, delivery.delivery_tag),
            requeue=False,
        )

        self._acknowledged = True

    async def requeue(self) -> None:
        if self._acknowledged:
            raise RuntimeError("message already acknowledged")

        delivery = cast(commands.Basic.Deliver, self._message.delivery)

        await self._message.channel.basic_nack(
            cast(int, delivery.delivery_tag),
            requeue=True,
        )

        self._acknowledged = True

    @property
    def routing_key(self) -> str:
        delivery = cast(commands.Basic.Deliver, self._message.delivery)

        return str(delivery.routing_key)


ConsumerCallback = Callable[[Message], Coroutine[None, None, None]]


class Consumer(object):
    def __init__(
        self,
        channel: abc.AbstractChannel,
        queue_name: str,
    ):
        self._channel = channel
        self._logger = get_logger(__name__)
        self._queue_name = queue_name

    async def consume(self, callback: ConsumerCallback) -> None:
        await self._channel.basic_consume(
            self._queue_name,
            self._decorate_callback(callback),
        )

        # basic_consume() doesn't block while it consumes
        await Event().wait()

    def _decorate_callback(
        self,
        callback: ConsumerCallback,
    ) -> abc.ConsumerCallback:
        @functools.wraps(callback)
        async def decorator(incoming: abc.DeliveredMessage) -> None:
            msg = Message(incoming)

            try:
                await callback(msg)
            except Exception:  # noqa: PIE786
                self._logger.exception()

                if not msg.acknowledged:
                    await msg.nack()
            else:
                if not msg.acknowledged:
                    await msg.ack()

            self._logger.info(
                "Message consumed.",
                queue=self._queue_name,
                routing_key=msg.routing_key,
                type=msg.body.DESCRIPTOR.full_name,
            )

        return decorator


async def create_consumer(
    conn: Connection,
    exchange_name: str,
    queue_name: str,
    routing_key: str,
    exchange_type: str = "topic",
) -> Consumer:
    channel = await conn.channel()

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
