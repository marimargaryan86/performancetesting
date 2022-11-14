import datetime
import time
from typing import TypeVar

import prometheus_client
import structlog
from google.protobuf import message
from sentry_sdk import Hub, tracing

from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.transport.amqp import protocol, types

_Proto = TypeVar("_Proto", bound=message.Message)
_label_names = ("exchange", "queue", "routing_key")

_histogram_processing_time = prometheus_client.Histogram(
    "amqp_consumer_processing_time_seconds",
    "Processing time of consumed messages (in seconds).",
    labelnames=_label_names,
    buckets=prometheus.BUCKETS,
)

_histogram_wait_time = prometheus_client.Histogram(
    "amqp_consumer_wait_time_seconds",
    "Wait time of consumed messages (in seconds).",
    labelnames=_label_names,
    buckets=prometheus.BUCKETS,
)

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

_counter_requeued_messages = prometheus_client.Counter(
    "amqp_consumer_requeued_messages_total",
    "Total number of requeued messages.",
    labelnames=_label_names,
)


def _prometheus_labels(msg: types.Message[_Proto]) -> dict[str, str]:
    return {
        "exchange": msg.exchange,
        "queue": msg.queue,
        "routing_key": msg.routing_key,
    }


async def observe_processing_time(
    msg: types.Message[_Proto],
    next_func: protocol.ConsumerFunc[_Proto],
) -> None:
    start_time = time.perf_counter()

    await next_func(msg)

    _histogram_processing_time.labels(**_prometheus_labels(msg)).observe(
        datetime.timedelta(seconds=time.perf_counter() - start_time).total_seconds(),
    )


async def observe_wait_time(
    msg: types.Message[_Proto],
    next_func: protocol.ConsumerFunc[_Proto],
) -> None:
    if msg.enqueued_at:
        _histogram_wait_time.labels(**_prometheus_labels(msg)).observe(
            (
                datetime.datetime.now(tz=datetime.timezone.utc) - msg.enqueued_at
            ).total_seconds(),
        )

    return await next_func(msg)


async def count_messages(
    msg: types.Message[_Proto],
    next_func: protocol.ConsumerFunc[_Proto],
) -> None:
    await next_func(msg)

    _counter_messages.labels(**_prometheus_labels(msg)).inc()

    if msg.status == types.MessageStatus.nacked:
        _counter_failed_messages.labels(**_prometheus_labels(msg)).inc()

    if msg.status == types.MessageStatus.requeued:
        _counter_requeued_messages.labels(**_prometheus_labels(msg)).inc()


async def with_sentry_context(
    msg: types.Message[_Proto],
    next_func: protocol.ConsumerFunc[_Proto],
) -> None:
    transaction = tracing.Transaction.continue_from_headers(
        {
            metadata_key: metadata_value
            for metadata_key, metadata_value in msg.headers.items()
        },
        op="amqp.message",
        name="{0}/{1}".format(msg.queue, msg.routing_key),
    )

    with Hub(Hub.current).start_transaction(transaction) as span:
        await next_func(msg)

        match msg.status:
            case types.MessageStatus.acked | types.MessageStatus.requeued:
                span.set_status("ok")
            case types.MessageStatus.nacked | types.MessageStatus.unprocessed:
                span.set_status("nok")


def auto_ack_and_nack_factory() -> protocol.ConsumerMiddleware[_Proto]:
    logger = structlog.get_logger(__name__)

    async def wrapper(
        msg: types.Message[_Proto],
        next_func: protocol.ConsumerFunc[_Proto],
    ) -> None:
        try:
            await next_func(msg)
        except Exception:  # noqa: PIE786
            logger.exception("An error occurred in consumer callback")
            await msg.nack()
        else:
            await msg.ack()

    return wrapper
