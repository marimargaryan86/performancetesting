from typing import Awaitable, Callable, Mapping, Protocol, TypeVar

from google.protobuf import message

from snowfall.stdlib.transport.amqp import types

_Proto = TypeVar("_Proto", bound=message.Message)
ConsumerCallback = Callable[[types.Message[_Proto]], Awaitable[None]]


class Consumer(Protocol[_Proto]):
    async def consume(self, callback: ConsumerCallback[_Proto]) -> None:
        """Consume a message from the queue."""


class Producer(Protocol):
    async def publish(
        self,
        msg: message.Message,
        routing_key: str,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Publish a message on the exchange."""
