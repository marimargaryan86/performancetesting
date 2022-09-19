from __future__ import annotations

import asyncio
import dataclasses
import os
from typing import Any, Callable, Coroutine, Mapping, Type, Union

from aio_pika import Message as PikeMessage
from aio_pika import abc, connect_robust
from google.protobuf import any_pb2, message, symbol_database
from sentry_sdk import Hub, tracing
from structlog import get_logger

from snowfall.stdlib.instrumentation.sentry import get_span

_SPAN_PRODUCER_OP = "amqp.produce"
_SPAN_CONSUMER_OP = "amqp.message"


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


async def create_connection(dsn: str) -> abc.AbstractRobustConnection:
    return await connect_robust(url=dsn)


class Producer(object):
    def __init__(
        self,
        connection: abc.AbstractConnection,
        exchange: Exchange,
    ):
        self._connection = connection
        self._exchange = exchange
        self._logger = get_logger(__name__)

    async def publish(self, msg: message.Message, routing_key: str) -> None:
        with get_span(
            _SPAN_PRODUCER_OP,
            "{0}/{1}".format(self._exchange.name, routing_key),
        ) as span:
            async with self._connection.channel() as channel:
                exchange = await channel.declare_exchange(
                    name=self._exchange.name,
                    type=self._exchange.type_,
                    durable=True,
                )

                await exchange.publish(
                    message=PikeMessage(
                        body=Serializer.serialize(msg),
                        headers={
                            header_key: header_value
                            for header_key, header_value in span.iter_headers()
                        },
                        content_type="application/x-protobuf",
                    ),
                    routing_key=routing_key,
                )

        self._logger.info(
            "Message published.",
            exchange=self._exchange.name,
            routing_key=routing_key,
            type=msg.DESCRIPTOR.full_name,
        )


class Message(object):
    def __init__(self, msg: abc.AbstractIncomingMessage):
        self.body = Serializer.deserialize(msg.body)
        self.headers: Mapping[str, Any] = msg.headers
        self._message = msg

    async def ack(self) -> None:
        if self.acknowledged:
            return

        await self._message.ack()

    @property
    def acknowledged(self) -> bool:
        return self._message.processed

    async def nack(self) -> None:
        if self.acknowledged:
            return

        await self._message.nack(requeue=False)

    async def requeue(self) -> None:
        if self.acknowledged:
            return

        await self._message.nack(requeue=True)

    @property
    def routing_key(self) -> str:
        return self._message.routing_key or ""


ConsumerCallback = Callable[[Message], Coroutine[None, None, None]]


@dataclasses.dataclass(frozen=True)
class Exchange(object):
    name: str
    type_: abc.ExchangeType = abc.ExchangeType.TOPIC


class Consumer(object):
    def __init__(
        self,
        connection: abc.AbstractConnection,
        exchange: Exchange,
        queue_name: str,
        routing_key: str,
    ):
        self._connection = connection
        self._exchange = exchange
        self._logger = get_logger(__name__)
        self._queue_name = queue_name
        self._routing_key = routing_key

    async def consume(self, callback: ConsumerCallback) -> None:
        async with self._connection.channel() as channel:
            await channel.set_qos(prefetch_count=os.cpu_count() or 1)

            exchange = await channel.declare_exchange(
                name=self._exchange.name,
                type=self._exchange.type_,
                durable=True,
            )

            queue = await channel.declare_queue(
                name=self._queue_name,
                durable=True,
            )

            await queue.bind(exchange, self._routing_key)
            await self._consume(queue, callback)

    async def _consume(
        self,
        queue: abc.AbstractQueue,
        callback: ConsumerCallback,
    ) -> None:
        async def wrapper(incoming: abc.AbstractIncomingMessage) -> None:
            await self._process(incoming, callback)

        await queue.consume(wrapper)
        await asyncio.Future()

    async def _process(
        self,
        incoming: abc.AbstractIncomingMessage,
        callback: ConsumerCallback,
    ) -> None:
        msg = Message(incoming)
        transaction = tracing.Transaction.continue_from_headers(
            {
                metadata_key: metadata_value
                for metadata_key, metadata_value in msg.headers.items()
            },
            op=_SPAN_CONSUMER_OP,
            name="{0}/{1}".format(self._queue_name, msg.routing_key),
        )

        with Hub(Hub.current).start_transaction(transaction) as span:
            span.set_status("ok")

            try:
                await callback(msg)
            except Exception:
                self._logger.exception()
                span.set_status("nok")
                await msg.nack()

                raise
            else:
                await msg.ack()
            finally:
                self._logger.info(
                    "Message consumed.",
                    queue=self._queue_name,
                    routing_key=msg.routing_key,
                    type=msg.body.DESCRIPTOR.full_name,
                )
