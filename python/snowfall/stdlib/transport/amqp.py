from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import datetime
import enum
import os
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Generic,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)

import prometheus_client
from aio_pika import Message as PikaMessage
from aio_pika import abc, connect_robust
from google.protobuf import message
from sentry_sdk import Hub, tracing
from structlog import get_logger

from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.instrumentation.sentry import get_span
from snowfall.stdlib.v1alpha import amqp_pb2

_SPAN_PRODUCER_OP = "amqp.produce"
_SPAN_CONSUMER_OP = "amqp.message"
_TRACKABLE_HEADERS = ("x-trackable-id", "x-trackable-routing-key")
_Proto = TypeVar("_Proto", bound=message.Message)
TrackableUpdateMessageType = Union[
    Type[amqp_pb2.TrackableReceived],
    Type[amqp_pb2.TrackableAcked],
    Type[amqp_pb2.TrackableNacked],
]


async def create_connection(dsn: str) -> abc.AbstractConnection:
    return await connect_robust(url=dsn)


@dataclasses.dataclass(frozen=True)
class TrackableMetadata(object):
    routing_key: str
    trackable_id: Optional[str] = None


class Producer(object):
    _counter_messages = prometheus_client.Counter(
        "amqp_producer_produced_messages_total",
        "Total number of produced messages.",
        labelnames=("exchange", "routing_key"),
    )

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
                    message=PikaMessage(
                        body=protobuf.AnySerializer.serialize(msg),
                        headers={
                            **headers,
                            **span_headers,
                            "x-enqueued-at": int(
                                datetime.datetime.now(
                                    tz=datetime.timezone.utc,
                                ).timestamp(),
                            ),
                        },
                        content_type="application/x-protobuf",
                    ),
                    routing_key=routing_key,
                )

                self._counter_messages.labels(
                    **self._prometheus_labels(routing_key),
                ).inc()

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
        trackable_id = trackable_metadata.trackable_id or string.uuid()
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

    def _prometheus_labels(self, routing_key: str) -> dict[str, str]:
        return {
            "exchange": self._exchange.name,
            "routing_key": routing_key,
        }


class _MessageStatus(enum.Enum):
    acked = "acked"
    nacked = "nacked"
    unhandled = "unhandled"


class Message(Generic[_Proto]):
    def __init__(self, msg: abc.AbstractIncomingMessage):
        self.body = protobuf.AnySerializer[_Proto].deserialize(msg.body)
        self.headers: Mapping[str, Any] = msg.headers
        self._message = msg
        self._status: _MessageStatus = _MessageStatus.unhandled

    async def ack(self) -> None:
        if self.processed:
            return

        await self._message.ack()
        self._status = _MessageStatus.acked

    @property
    def enqueued_at(self) -> datetime.datetime | None:
        try:
            enqueued_at = self.headers["x-enqueued-at"]
        except KeyError:
            return None

        return datetime.datetime.fromtimestamp(enqueued_at, tz=datetime.timezone.utc)

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


ConsumerCallback = Callable[
    [Message[_Proto]],
    Coroutine[None, None, None],
]


@dataclasses.dataclass(frozen=True)
class Exchange(object):
    name: str
    type_: abc.ExchangeType = abc.ExchangeType.TOPIC


def _is_trackable(msg: Message[_Proto]) -> bool:
    return all(header in msg.headers for header in _TRACKABLE_HEADERS)


class _TrackableManager(object):
    def __init__(self, producer: Producer) -> None:
        self._producer = producer

    async def message_received(self, msg: Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableReceived)

    async def message_acked(self, msg: Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableAcked)

    async def message_nacked(self, msg: Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableNacked)

    async def _report(
        self,
        msg: Message[_Proto],
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
    msg: Message[_Proto],
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
    _counter_messages = prometheus_client.Counter(
        "amqp_consumer_consumed_messages_total",
        "Total number of consumed messages.",
        labelnames=("exchange", "queue", "routing_key"),
    )

    _counter_failed_messages = prometheus_client.Counter(
        "amqp_consumer_failed_messages_total",
        "Total number of failed messages.",
        labelnames=("exchange", "queue", "routing_key"),
    )

    _histogram_wait_time = prometheus_client.Histogram(
        "amqp_consumer_wait_time_seconds",
        "Wait time of consumed messages (in seconds).",
        labelnames=("exchange", "queue", "routing_key"),
        buckets=prometheus.BUCKETS,
    )

    _histogram_processing_time = prometheus_client.Histogram(
        "amqp_consumer_processing_time_seconds",
        "Processing time of consumed messages (in seconds).",
        labelnames=("exchange", "queue", "routing_key"),
        buckets=prometheus.BUCKETS,
    )

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

    async def consume(self, callback: ConsumerCallback[_Proto]) -> None:
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
        callback: ConsumerCallback[_Proto],
    ) -> None:
        async def wrapper(incoming: abc.AbstractIncomingMessage) -> None:
            try:
                await self._process(incoming, callback)
            except Exception:  # noqa: PIE786
                self._logger.exception("An error occurred while processing message")

        await queue.consume(wrapper)
        await asyncio.Future()

    async def _process(
        self,
        incoming: abc.AbstractIncomingMessage,
        callback: ConsumerCallback[_Proto],
    ) -> None:
        msg = Message[_Proto](incoming)

        if msg.enqueued_at:
            self._track_wait_time(msg.enqueued_at)

        with self._with_transaction(msg) as span:
            async with _manage_trackable(
                msg=msg,
                producer=Producer(self._connection, self._exchange),
            ):
                span.set_status("ok")
                start_time = datetime.datetime.now(tz=datetime.timezone.utc)

                try:
                    await callback(msg)
                except Exception:  # noqa: PIE786
                    self._logger.exception("An error occurred in consumer callback")
                    span.set_status("nok")
                    await msg.nack()
                else:
                    await msg.ack()
                finally:
                    self._finalize_message(msg, start_time)

    def _with_transaction(self, msg: Message[_Proto]) -> tracing.Transaction:
        transaction = tracing.Transaction.continue_from_headers(
            {
                metadata_key: metadata_value
                for metadata_key, metadata_value in msg.headers.items()
            },
            op=_SPAN_CONSUMER_OP,
            name="{0}/{1}".format(self._queue_name, msg.routing_key),
        )

        return Hub(Hub.current).start_transaction(transaction)

    @property
    def _prometheus_labels(self) -> dict[str, str]:
        return {
            "exchange": self._exchange.name,
            "queue": self._queue_name,
            "routing_key": self._routing_key,
        }

    def _finalize_message(
        self,
        msg: Message[_Proto],
        start_time: datetime.datetime,
    ) -> None:
        self._track_processing_time(start_time)
        self._counter_messages.labels(**self._prometheus_labels).inc()

        if not msg.acknowledged:
            self._counter_failed_messages.labels(
                **self._prometheus_labels,
            ).inc()

        self._logger.info(
            "Message consumed.",
            queue=self._queue_name,
            routing_key=msg.routing_key,
            type=msg.body.DESCRIPTOR.full_name,
        )

    def _track_processing_time(self, start_time: datetime.datetime) -> None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        self._histogram_processing_time.labels(**self._prometheus_labels).observe(
            (start_time - now).total_seconds(),
        )

    def _track_wait_time(self, enqueued_at: datetime.datetime) -> None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        self._histogram_wait_time.labels(**self._prometheus_labels).observe(
            (now - enqueued_at).total_seconds(),
        )
