from __future__ import annotations

import abc
import asyncio
import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from google.protobuf import message

from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import protocol, types
from snowfall.stdlib.v1 import amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
_Record_co = TypeVar("_Record_co", covariant=True)
TRACKABLE_ID = "x-trackable-id"
TRACKABLE_ROUTING_KEY = "x-trackable-routing-key"
_TRACKABLE_HEADERS = (TRACKABLE_ID, TRACKABLE_ROUTING_KEY)
_skippable_statuses = (
    amqp_pb2.Trackable.STATUS_FAILED,
    amqp_pb2.Trackable.STATUS_COMPLETED,
    amqp_pb2.Trackable.STATUS_UNSPECIFIED,
)


def _is_trackable(headers: Mapping[str, Any]) -> bool:
    return all(header in headers for header in _TRACKABLE_HEADERS)


def to_tracking_key(routing_key: str) -> str:
    return "trackable.{0}".format(
        routing_key,
    )


async def _get_status_stats(
    status_hash: redis_types.Hash[str],
) -> tuple[int, int, int]:
    received, acked, nacked = await asyncio.gather(
        status_hash.get(
            protobuf.enum_value_to_slug(
                amqp_pb2.Trackable.Event.DESCRIPTOR,
                amqp_pb2.Trackable.EVENT_RECEIVED,
            ),
        ),
        status_hash.get(
            protobuf.enum_value_to_slug(
                amqp_pb2.Trackable.Event.DESCRIPTOR,
                amqp_pb2.Trackable.EVENT_ACKED,
            ),
        ),
        status_hash.get(
            protobuf.enum_value_to_slug(
                amqp_pb2.Trackable.Event.DESCRIPTOR,
                amqp_pb2.Trackable.EVENT_NACKED,
            ),
        ),
    )

    return (
        int(received or 0),
        int(acked or 0),
        int(nacked or 0),
    )


class _AbstractStatusHandler(abc.ABC):
    def __init__(self, redis: redis_types.Client[str]) -> None:
        self._redis = redis

    async def on_message(self, msg: amqp_pb2.Trackable) -> None:
        status, expiry_at = await self._get_status_and_expiry_by_id(msg.id)

        if status in _skippable_statuses:
            return

        status_hash = self._redis.hash_(
            "offer_searches.{0}.statuses".format(msg.id),
        )

        await status_hash.increment(
            protobuf.enum_value_to_slug(
                amqp_pb2.Trackable.Event.DESCRIPTOR,
                msg.event,
            ),
        )

        await asyncio.gather(
            self._determine_status(msg, status, status_hash),
            redis_types.put_expires_at_if_less_than_current(
                self._redis,
                status_hash,
                expiry_at,
            ),
        )

    @abc.abstractmethod
    async def _determine_status(
        self,
        msg: amqp_pb2.Trackable,
        current_status: amqp_pb2.Trackable.Status.ValueType,
        status_hash: redis_types.Hash[str],
    ) -> None:
        """Determine the new status, if any.

        Should call the _on_* methods on change.
        """

    @abc.abstractmethod
    async def _get_status_and_expiry_by_id(
        self,
        trackable_id: str,
    ) -> tuple[amqp_pb2.Trackable.Status.ValueType, datetime.datetime]:
        """Get the current status and expiry date by its trackable ID.

        Should return `STATUS_UNSPECIFIED` and `datetime.now()` if unknown.
        """

    @abc.abstractmethod
    async def _on_completed(self, msg: amqp_pb2.Trackable) -> None:
        """Logic to run when the status changes to 'completed'."""

    @abc.abstractmethod
    async def _on_failed(self, msg: amqp_pb2.Trackable) -> None:
        """Logic to run when the status changes to 'failed'."""

    @abc.abstractmethod
    async def _on_processing(self, msg: amqp_pb2.Trackable) -> None:
        """Logic to run when the status changes to 'processing'."""


class FixedSizeStatusHandler(_AbstractStatusHandler):
    async def set_expected_size(
        self,
        trackable_id: str,
        size: int,
    ) -> None:
        status_hash = self._redis.hash_(
            "offer_searches.{0}.statuses".format(trackable_id),
        )

        await status_hash.put("expected", size)

    async def _determine_status(
        self,
        msg: amqp_pb2.Trackable,
        current_status: amqp_pb2.Trackable.Status.ValueType,
        status_hash: redis_types.Hash[str],
    ) -> None:
        expected = int(await status_hash.get("expected") or 0)
        _, acked, nacked = await _get_status_stats(status_hash)

        if nacked > 0:
            await self._on_failed(msg)
        elif acked >= expected:
            await self._on_completed(msg)
        elif current_status == amqp_pb2.Trackable.STATUS_PENDING:
            await self._on_processing(msg)


class AnySizeStatusHandler(_AbstractStatusHandler):
    async def _determine_status(
        self,
        msg: amqp_pb2.Trackable,
        current_status: amqp_pb2.Trackable.Status.ValueType,
        status_hash: redis_types.Hash[str],
    ) -> None:
        received, acked, nacked = await _get_status_stats(status_hash)

        if nacked > 0:
            await self._on_failed(msg)
        elif acked >= received:
            await self._on_completed(msg)
        elif current_status == amqp_pb2.Trackable.STATUS_PENDING:
            await self._on_processing(msg)


class StatusReporter(object):
    def __init__(self, producer: protocol.Producer) -> None:
        self._producer = producer

    async def receive(self, headers: Mapping[str, Any]) -> None:
        await self._report(headers, amqp_pb2.Trackable.EVENT_RECEIVED)

    async def ack(self, headers: Mapping[str, Any]) -> None:
        await self._report(headers, amqp_pb2.Trackable.EVENT_ACKED)

    async def nack(self, headers: Mapping[str, Any]) -> None:
        await self._report(headers, amqp_pb2.Trackable.EVENT_NACKED)

    async def _report(
        self,
        headers: Mapping[str, Any],
        event: amqp_pb2.Trackable.Event.ValueType,
    ) -> None:
        if not _is_trackable(headers):
            return

        trackable = amqp_pb2.Trackable(
            id=headers[TRACKABLE_ID],
            event=event,
        )

        await self._producer.publish(
            msg=trackable,
            routing_key=headers[TRACKABLE_ROUTING_KEY],
        )


class ReportingMiddleware(object):
    def __init__(self, status_reporter: StatusReporter) -> None:
        self._status_reporter = status_reporter

    async def execute(
        self,
        msg: types.Message[_Proto],
        next_func: protocol.ConsumerFunc[_Proto],
    ) -> None:
        await self._status_reporter.receive(msg.headers)
        await next_func(msg)

        if msg.acknowledged:
            await self._status_reporter.ack(msg.headers)
        elif not msg.requeued:
            await self._status_reporter.nack(msg.headers)


class TrackableProducer(protocol.Producer):
    def __init__(self, producer: protocol.Producer) -> None:
        self._producer = producer

    async def publish(  # noqa: WPS211
        self,
        msg: message.Message,
        routing_key: str,
        expiration: datetime.timedelta | datetime.datetime | None = None,
        headers: Mapping[str, str] | None = None,
        trackable_id: str | None = None,
        trackable_routing_key: str | None = None,
    ) -> None:
        headers = headers or {}
        trackable_id = trackable_id or string.uuid()
        trackable_routing_key = trackable_routing_key or to_tracking_key(routing_key)

        return await self._producer.publish(
            msg=msg,
            routing_key=routing_key,
            expiration=expiration,
            headers={
                **headers,
                TRACKABLE_ID: trackable_id,
                TRACKABLE_ROUTING_KEY: trackable_routing_key,
            },
        )
