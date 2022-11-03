from __future__ import annotations

import contextlib
import functools
from typing import AsyncGenerator, Mapping, TypeVar

from google.protobuf import message

from snowfall.stdlib import string
from snowfall.stdlib.transport.amqp import protocol, types
from snowfall.stdlib.v1alpha import amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
_TRACKABLE_HEADERS = ("x-trackable-id", "x-trackable-routing-key")


def _is_trackable(msg: types.Message[_Proto]) -> bool:
    return all(header in msg.headers for header in _TRACKABLE_HEADERS)


class StatusReporter(object):
    def __init__(self, producer: protocol.Producer) -> None:
        self._producer = producer

    async def receive(self, msg: types.Message[_Proto]) -> None:
        await self._report(
            msg,
            amqp_pb2.Trackable(event=amqp_pb2.Trackable.EVENT_RECEIVED),
        )

    async def ack(self, msg: types.Message[_Proto]) -> None:
        await self._report(
            msg,
            amqp_pb2.Trackable(event=amqp_pb2.Trackable.EVENT_ACKED),
        )

    async def nack(self, msg: types.Message[_Proto]) -> None:
        await self._report(
            msg,
            amqp_pb2.Trackable(event=amqp_pb2.Trackable.EVENT_NACKED),
        )

    async def _report(
        self,
        msg: types.Message[_Proto],
        trackable: amqp_pb2.Trackable,
    ) -> None:
        if not _is_trackable(msg):
            return

        trackable.id = msg.headers["x-trackable-id"]

        await self._producer.publish(
            msg=trackable,
            routing_key=msg.headers["x-trackable-routing-key"],
        )


@contextlib.asynccontextmanager
async def report_status(
    status_reporter: StatusReporter,
    msg: types.Message[_Proto],
) -> AsyncGenerator[None, None]:
    await status_reporter.receive(msg)

    try:
        yield
    finally:
        if msg.acknowledged:
            await status_reporter.ack(msg)
        else:
            await status_reporter.nack(msg)


class Consumer(protocol.Consumer):
    def __init__(
        self,
        consumer: protocol.Consumer,
        producer: protocol.Producer,
    ) -> None:
        self._consumer = consumer
        self._status_reporter = StatusReporter(producer)

    async def consume(self, callback: protocol.ConsumerCallback[_Proto]) -> None:
        @functools.wraps(callback)
        async def wrapper(msg: types.Message[_Proto]) -> None:
            async with report_status(self._status_reporter, msg):
                return await callback(msg)

        return await self._consumer.consume(wrapper)


class Producer(protocol.Producer):
    def __init__(self, producer: protocol.Producer) -> None:
        self._producer = producer

    async def publish(  # noqa: WPS211
        self,
        msg: message.Message,
        routing_key: str,
        headers: Mapping[str, str] | None = None,
        trackable_id: str | None = None,
        trackable_routing_key: str | None = None,
    ) -> None:
        headers = headers or {}
        trackable_id = trackable_id or string.uuid()
        trackable_routing_key = trackable_routing_key or "trackable.{0}".format(
            routing_key,
        )

        return await self._producer.publish(
            msg=msg,
            routing_key=routing_key,
            headers={
                **headers,
                "x-trackable-id": trackable_id,
                "x-trackable-routing-key": trackable_routing_key,
            },
        )
