from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import enum
import os
import uuid
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Mapping,
    Optional,
    Type,
    Union,
)

from aio_pika import Message as PikeMessage
from aio_pika import abc, connect_robust
from google.protobuf import any_pb2, message, symbol_database
from sentry_sdk import Hub, tracing
from structlog import get_logger

from snowfall.stdlib.instrumentation.sentry import get_span
from snowfall.stdlib.v1alpha import amqp_pb2

_SPAN_PRODUCER_OP = "amqp.produce"
_SPAN_CONSUMER_OP = "amqp.message"
_TRACKABLE_HEADERS = ("x-trackable-id", "x-trackable-routing-key")
TrackableUpdateMessageType = Union[
    Type[amqp_pb2.TrackableReceived],
    Type[amqp_pb2.TrackableAcked],
    Type[amqp_pb2.TrackableNacked],
]


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


@dataclasses.dataclass(frozen=True)
class TrackableMetadata(object):
    routing_key: str
    trackable_id: Optional[str] = None


class Producer(object):
    def __init__(
        self,
        connection: abc.AbstractConnection,
        exchange: Exchange,
    ):
        self._connection = connection
        self._exchange = exchange
        self._logger = get_logger(__name__)

    async def publish(  # noqa: WPS210
        self,
        msg: message.Message,
        routing_key: str,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
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

                span_headers = {
                    header_key: header_value
                    for header_key, header_value in span.iter_headers()
                }
                headers = headers or {}

                await exchange.publish(
                    message=PikeMessage(
                        body=Serializer.serialize(msg),
                        headers={**span_headers, **headers},
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

    async def publish_trackable(
        self,
        msg: message.Message,
        routing_key: str,
        trackable_metadata: TrackableMetadata,
        headers: Optional[Mapping[str, str]] = None,
    ) -> str:
        trackable_id = trackable_metadata.trackable_id or str(uuid.uuid4())
        headers = headers or {}

        await self.publish(
            msg=msg,
            routing_key=routing_key,
            headers={
                **headers,
                "x-trackable-id": trackable_id,
                "x-trackable-routing-key": trackable_metadata.routing_key,
            },
        )

        return trackable_id


class _MessageStatus(enum.Enum):
    acked = "acked"
    nacked = "nacked"
    unhandled = "unhandled"


class Message(object):
    def __init__(self, msg: abc.AbstractIncomingMessage):
        self.body = Serializer.deserialize(msg.body)
        self.headers: Mapping[str, Any] = msg.headers
        self._message = msg
        self._status: _MessageStatus = _MessageStatus.unhandled

    async def ack(self) -> None:
        if self.processed:
            return

        await self._message.ack()
        self._status = _MessageStatus.acked

    @property
    def processed(self) -> bool:
        return self._message.processed

    @property
    def acknowledged(self) -> bool:
        return self._status == _MessageStatus.acked

    async def nack(self) -> None:
        if self.processed:
            return

        await self._message.nack(requeue=False)
        self._status = _MessageStatus.nacked

    async def requeue(self) -> None:
        if self.processed:
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


def _is_trackable(msg: Message) -> bool:
    return all(header in msg.headers for header in _TRACKABLE_HEADERS)


class _TrackableManager(object):
    def __init__(self, producer: Producer) -> None:
        self._producer = producer

    async def message_received(self, msg: Message) -> None:
        await self._report(msg, amqp_pb2.TrackableReceived)

    async def message_acked(self, msg: Message) -> None:
        await self._report(msg, amqp_pb2.TrackableAcked)

    async def message_nacked(self, msg: Message) -> None:
        await self._report(msg, amqp_pb2.TrackableNacked)

    async def _report(
        self,
        msg: Message,
        proto_class: TrackableUpdateMessageType,
    ) -> None:
        if not _is_trackable(msg):
            return

        await self._producer.publish(
            msg=proto_class(
                id=msg.headers["x-trackable-id"],
            ),
            routing_key=msg.headers["x-trackable-routing-key"],
        )


@contextlib.asynccontextmanager
async def _manage_trackable(
    msg: Message,
    producer: Producer,
) -> AsyncGenerator[None, None]:
    trackable_manager = _TrackableManager(producer)

    await trackable_manager.message_received(msg)

    try:
        yield
    finally:
        if msg.acknowledged:
            await trackable_manager.message_acked(msg)
        else:
            await trackable_manager.message_nacked(msg)


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
            await channel.set_qos(
                prefetch_count=((os.cpu_count() or 1) * 2) + 1,
            )

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
            async with _manage_trackable(
                msg=msg,
                producer=Producer(self._connection, self._exchange),
            ):
                span.set_status("ok")

                try:
                    await callback(msg)
                except Exception:  # noqa: PIE786
                    self._logger.exception()
                    span.set_status("nok")
                    await msg.nack()
                else:
                    await msg.ack()
                finally:
                    self._logger.info(
                        "Message consumed.",
                        queue=self._queue_name,
                        routing_key=msg.routing_key,
                        type=msg.body.DESCRIPTOR.full_name,
                    )
