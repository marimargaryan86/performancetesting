from __future__ import annotations

import asyncio
import datetime
import os
from typing import Awaitable, Callable, TypeVar

import prometheus_client
from aio_pika import abc
from google.protobuf import message
from sentry_sdk import Hub, tracing
from structlog import get_logger

from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.amqp.producer import Producer
from snowfall.stdlib.transport.amqp.trackable import manage_trackable

_SPAN_CONSUMER_OP = "amqp.message"
_label_names = ("exchange", "queue", "routing_key")
_Proto = TypeVar("_Proto", bound=message.Message)
ConsumerCallback = Callable[
    [types.Message[_Proto]],
    Awaitable[None],
]


class Consumer(object):  # noqa: WPS214
    _counter_messages = prometheus_client.Counter(
        "amqp_consumer_consumed_messages_total",
        "Total number of consumed messages.",
        labelnames=_label_names,
    )

    _counter_failed_messages = prometheus_client.Counter(
        "amqp_consumer_failed_messages_total",
        "Total number of failed messages.",
        labelnames=_label_names,
    )

    _histogram_wait_time = prometheus_client.Histogram(
        "amqp_consumer_wait_time_seconds",
        "Wait time of consumed messages (in seconds).",
        labelnames=_label_names,
        buckets=prometheus.BUCKETS,
    )

    _histogram_processing_time = prometheus_client.Histogram(
        "amqp_consumer_processing_time_seconds",
        "Processing time of consumed messages (in seconds).",
        labelnames=_label_names,
        buckets=prometheus.BUCKETS,
    )

    def __init__(
        self,
        connection: abc.AbstractConnection,
        exchange: types.Exchange,
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
        msg = types.Message[_Proto](incoming)

        if msg.enqueued_at:
            self._track_wait_time(msg.enqueued_at)

        with self._with_transaction(msg) as span:
            async with manage_trackable(
                msg=msg,
                producer_obj=Producer(self._connection, self._exchange),
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

    def _with_transaction(self, msg: types.Message[_Proto]) -> tracing.Transaction:
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
        msg: types.Message[_Proto],
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
            (now - start_time).total_seconds(),
        )

    def _track_wait_time(self, enqueued_at: datetime.datetime) -> None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        self._histogram_wait_time.labels(**self._prometheus_labels).observe(
            (now - enqueued_at).total_seconds(),
        )
