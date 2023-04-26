import datetime
from typing import Awaitable, Callable, Mapping, Protocol, TypeVar

from google.protobuf import message

from snowfall.stdlib.transport.amqp import types

_Proto = TypeVar("_Proto", bound=message.Message)
ConsumerFunc = Callable[[types.Message[_Proto]], Awaitable[None]]
ConsumerMiddleware = Callable[
    [types.Message[_Proto], ConsumerFunc[_Proto]],
    Awaitable[None],
]


class Consumer(Protocol[_Proto]):
    async def consume(self, callback: ConsumerFunc[_Proto]) -> None:
        """Consume a message from the queue."""


class Producer(Protocol):
    async def publish(
        self,
        msg: message.Message,
        routing_key: str,
        expiration: datetime.timedelta | datetime.datetime | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Publish a message on the exchange."""
