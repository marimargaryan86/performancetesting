from __future__ import annotations

import contextlib
import dataclasses
from typing import AsyncGenerator, Mapping, Type, TypeVar, Union

from google.protobuf import message

from snowfall.stdlib import string
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.stdlib.v1alpha import amqp_pb2

TrackableUpdateMessageType = Union[
    Type[amqp_pb2.TrackableReceived],
    Type[amqp_pb2.TrackableAcked],
    Type[amqp_pb2.TrackableNacked],
]

_Proto = TypeVar("_Proto", bound=message.Message)
_TRACKABLE_HEADERS = ("x-trackable-id", "x-trackable-routing-key")


@dataclasses.dataclass(frozen=True)
class TrackableMetadata(object):
    routing_key: str
    trackable_id: str | None = None


def _is_trackable(msg: types.Message[_Proto]) -> bool:
    return all(header in msg.headers for header in _TRACKABLE_HEADERS)


class _TrackableManager(object):
    def __init__(self, producer_obj: producer.Producer) -> None:
        self._producer = producer_obj

    async def message_received(self, msg: types.Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableReceived)

    async def message_acked(self, msg: types.Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableAcked)

    async def message_nacked(self, msg: types.Message[_Proto]) -> None:
        await self._report(msg, amqp_pb2.TrackableNacked)

    async def _report(
        self,
        msg: types.Message[_Proto],
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
async def manage_trackable(
    msg: types.Message[_Proto],
    producer_obj: producer.Producer,
) -> AsyncGenerator[None, None]:
    trackable_manager = _TrackableManager(producer_obj)

    await trackable_manager.message_received(msg)

    try:
        yield
    finally:
        if msg.acknowledged:
            await trackable_manager.message_acked(msg)
        else:
            await trackable_manager.message_nacked(msg)


async def publish_trackable(
    msg: _Proto,
    routing_key: str,
    trackable_metadata: TrackableMetadata,
    headers: Mapping[str, str] | None = None,
) -> dict[str, dict[str, str] | str | _Proto]:
    trackable_id = trackable_metadata.trackable_id or string.uuid()
    headers = headers or {}

    return {
        "msg": msg,
        "routing_key": routing_key,
        "headers": {
            **headers,
            "x-trackable-id": trackable_id,
            "x-trackable-routing-key": trackable_metadata.routing_key,
        },
    }
