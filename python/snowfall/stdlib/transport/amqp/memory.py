import dataclasses
import datetime
import queue
from collections.abc import Mapping

from google.protobuf import message

from snowfall.stdlib.transport.amqp import protocol


@dataclasses.dataclass(frozen=True)
class _MessageContainer(object):
    message: message.Message
    routing_key: str
    expiration: datetime.datetime | None
    headers: Mapping[str, str]

    def is_expired(self) -> bool:
        if not self.expiration:
            return False

        return self.expiration < datetime.datetime.now(tz=datetime.UTC)


class Producer(protocol.Producer):
    def __init__(self) -> None:
        self._messages: queue.SimpleQueue[_MessageContainer] = queue.SimpleQueue()

    async def publish(
        self,
        msg: message.Message,
        routing_key: str,
        expiration: datetime.timedelta | datetime.datetime | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        if isinstance(expiration, datetime.timedelta):
            expiration = datetime.datetime.now(tz=datetime.UTC) + expiration

        self._messages.put_nowait(
            _MessageContainer(
                message=msg,
                routing_key=routing_key,
                expiration=expiration,
                headers=headers or {},
            ),
        )

    def len(self) -> int:
        return self._messages.qsize()

    def pop(self) -> _MessageContainer:
        return self._messages.get_nowait()
