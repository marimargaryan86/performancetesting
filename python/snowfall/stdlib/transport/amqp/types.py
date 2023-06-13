import dataclasses
import datetime
import enum
from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from aio_pika import abc, connection, robust_connection
from google.protobuf import message

from snowfall.stdlib.format import protobuf

_Proto = TypeVar("_Proto", bound=message.Message)


class Connection(robust_connection.RobustConnection):
    def __init__(
        self,
        url: str,
        timeout: datetime.timedelta | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        self._timeout = timeout

        super().__init__(connection.make_url(url), *args, **kwargs)

    async def __aenter__(self) -> "Connection":
        await self.connect(
            timeout=self._timeout.total_seconds() if self._timeout else None,
        )

        return self


ExchangeType = abc.ExchangeType


@dataclasses.dataclass(frozen=True)
class Exchange(object):
    name: str
    type_: ExchangeType = ExchangeType.TOPIC


class MessageStatus(enum.IntEnum):
    unprocessed = 0
    acked = 1
    nacked = 2
    requeued = 3


@dataclasses.dataclass(init=False)  # noqa: SF10
class Message(Generic[_Proto]):  # noqa: WPS214
    body: _Proto
    headers: Mapping[str, Any]
    status: MessageStatus

    def __init__(self, msg: abc.AbstractIncomingMessage, queue_name: str) -> None:
        self.body = protobuf.AnySerializer[_Proto].deserialize(msg.body)
        self.headers = msg.headers
        self._message = msg
        self._queue = queue_name
        self.status = MessageStatus.unprocessed

    async def ack(self) -> None:
        if self.processed:
            return

        await self._message.ack()
        self.status = MessageStatus.acked

    @property
    def enqueued_at(self) -> datetime.datetime | None:
        try:
            enqueued_at = self.headers["x-enqueued-at"]
        except KeyError:
            return None

        return datetime.datetime.fromtimestamp(enqueued_at, tz=datetime.UTC)

    @property
    def exchange(self) -> str:
        return self._message.exchange or ""

    @property
    def processed(self) -> bool:
        return self._message.processed

    @property
    def acknowledged(self) -> bool:
        return self.status == MessageStatus.acked

    @property
    def queue(self) -> str:
        return self._queue

    @property
    def requeued(self) -> bool:
        return self.status == MessageStatus.requeued

    async def nack(self, requeue: bool = False) -> None:
        if self.processed:
            return

        # TODO: make sure we don't requeue forever?
        await self._message.nack(requeue=requeue)
        self.status = MessageStatus.requeued if requeue else MessageStatus.nacked

    @property
    def routing_key(self) -> str:
        return self._message.routing_key or ""
