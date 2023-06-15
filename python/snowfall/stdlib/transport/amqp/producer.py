from __future__ import annotations

import datetime
from collections.abc import Mapping

import prometheus_client
from aio_pika import Message as PikaMessage
from aio_pika import abc
from google.protobuf import message

from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation.sentry import get_span
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import protocol, types

_SPAN_PRODUCER_OP = "amqp.produce"


class Producer(protocol.Producer):
    _counter_messages = prometheus_client.Counter(
        "amqp_producer_produced_messages_total",
        "Total number of produced messages.",
        labelnames=("exchange", "routing_key"),
    )

    def __init__(
        self,
        connection: abc.AbstractConnection,
        exchange: types.Exchange,
    ):
        self._connection = connection
        self._exchange = exchange
        self._logger = stdout.get_logger()

    async def publish(
        self,
        msg: message.Message,
        routing_key: str,
        expiration: datetime.timedelta | datetime.datetime | None = None,
        headers: Mapping[str, str] | None = None,
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

                span_headers = dict(span.iter_headers())
                headers = headers or {}

                await exchange.publish(
                    message=PikaMessage(
                        body=protobuf.AnySerializer.serialize(msg),
                        headers={
                            **headers,
                            **span_headers,
                            "x-enqueued-at": int(
                                datetime.datetime.now(
                                    tz=datetime.UTC,
                                ).timestamp(),
                            ),
                        },
                        expiration=expiration,
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

    def _prometheus_labels(self, routing_key: str) -> dict[str, str]:
        return {
            "exchange": self._exchange.name,
            "routing_key": routing_key,
        }
