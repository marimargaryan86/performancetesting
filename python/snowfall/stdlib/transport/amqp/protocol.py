import datetime
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Protocol, TypeVar

from google.protobuf import message
from pamqp import common

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


class Queue(Protocol[_Proto]):
    @property
    def arguments(self) -> common.Arguments:
        """Additional arguments to send to RabbitMQ when declaring the queue."""

    @property
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        """A sequence of exchanges and routing keys to bind the queue to."""

    @property
    def middlewares(self) -> Sequence[ConsumerMiddleware[_Proto]]:
        """A sequence of middlewares to wrap around the queue."""

    @property
    def name(self) -> str:
        """The name of the queue."""

    async def on_message(self, msg: types.Message[_Proto]) -> None:
        """Called by the consumer whenever a new message is received on the queue."""
