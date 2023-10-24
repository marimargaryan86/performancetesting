from __future__ import annotations

import abc
import asyncio
import contextlib
import os
from collections.abc import Awaitable, Callable, Hashable, Sequence
from typing import Generic, TypeVar, cast

from aio_pika import abc as aio_pika
from google.protobuf import message
from pamqp import common

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import middlewares, protocol, types

_Proto = TypeVar("_Proto", bound=message.Message)


class QueueConsumer(Generic[_Proto]):
    _default_middlewares: tuple[protocol.ConsumerMiddleware[_Proto], ...] = (
        middlewares.with_sentry_context,
        middlewares.count_messages,
        middlewares.observe_wait_time,
        middlewares.observe_processing_time,
        middlewares.auto_ack_and_nack_factory(),
    )

    def __init__(
        self,
        connection: aio_pika.AbstractConnection,
        queues: Sequence[protocol.Queue[_Proto]],
    ):
        self._connection = connection
        self._logger = stdout.get_logger()
        self._queues = queues
        # This is used just to hold references to queues etc. that would be
        # garbage collected otherwise, due to aio-pika using a WeakSet internally.
        self._refs: set[Hashable] = set()

    async def consume(self) -> None:
        async with contextlib.AsyncExitStack() as stack:
            for queue in self._queues:
                channel = cast(
                    aio_pika.AbstractChannel,
                    await stack.enter_async_context(self._connection.channel()),  # type: ignore[arg-type]
                )
                _, declared_queue = await asyncio.gather(
                    channel.set_qos(
                        prefetch_count=((os.cpu_count() or 1) * 2) + 1,
                        global_=True,
                    ),
                    channel.declare_queue(
                        name=queue.name,
                        durable=True,
                        arguments=queue.arguments,
                    ),
                )

                self._refs.add(declared_queue)
                await self._bind_queue(channel, declared_queue, queue.binds)
                await declared_queue.consume(self._generate_consumer(queue))
                self._logger.info(
                    "Queue consumer started.",
                    queue=queue.name,
                    binds=queue.binds,
                )

            await asyncio.Future()

    async def _bind_queue(
        self,
        channel: aio_pika.AbstractChannel,
        queue: aio_pika.AbstractQueue,
        binds: Sequence[tuple[types.Exchange, str]],
    ) -> None:
        for exchange, routing_key in binds:
            declared_exchange = await channel.declare_exchange(
                name=exchange.name,
                type=exchange.type_,
                durable=True,
            )

            self._refs.add(declared_exchange)
            await queue.bind(
                declared_exchange,
                routing_key,
            )

    def _generate_consumer(
        self,
        queue: protocol.Queue[_Proto],
    ) -> Callable[[aio_pika.AbstractIncomingMessage], Awaitable[None]]:
        def factory(
            middleware_func: protocol.ConsumerMiddleware[_Proto],
            inner_func: protocol.ConsumerFunc[_Proto],
        ) -> protocol.ConsumerFunc[_Proto]:
            async def decorator(message_obj: types.Message[_Proto]) -> None:
                return await middleware_func(message_obj, inner_func)

            return decorator

        func = cast(
            Callable[[types.Message[_Proto]], Awaitable[None]],
            queue.on_message,
        )
        middlewares_stack = cast(
            list[protocol.ConsumerMiddleware[_Proto]],
            list(
                reversed(
                    [
                        *self._default_middlewares,
                        *queue.middlewares,
                    ],
                ),
            ),
        )

        for middleware in middlewares_stack:
            func = factory(middleware, func)

        async def wrapper(incoming: aio_pika.AbstractIncomingMessage) -> None:
            msg = types.Message[_Proto](incoming, queue.name)

            try:
                await func(msg)
            except Exception:
                self._logger.exception(
                    "An error occurred while processing message",
                    type=msg.body.DESCRIPTOR.full_name,
                )
            else:
                self._logger.info(
                    "Message processed.",
                    type=msg.body.DESCRIPTOR.full_name,
                )

        return wrapper


class AbstractQueue(abc.ABC, protocol.Queue[_Proto]):
    @property
    def arguments(self) -> common.Arguments:
        """Additional arguments to send to RabbitMQ when declaring the queue."""

    @property
    @abc.abstractmethod
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        """A sequence of exchanges and routing keys to bind the queue to."""

    @property
    def middlewares(self) -> Sequence[protocol.ConsumerMiddleware[_Proto]]:
        return []

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the queue."""

    @abc.abstractmethod
    async def on_message(self, msg: types.Message[_Proto]) -> None:
        """Called by the consumer whenever a new message is received on the queue."""


class Consumer(protocol.Consumer[_Proto]):
    _default_middlewares: tuple[protocol.ConsumerMiddleware[_Proto], ...] = (
        middlewares.with_sentry_context,
        middlewares.count_messages,
        middlewares.observe_wait_time,
        middlewares.observe_processing_time,
        middlewares.auto_ack_and_nack_factory(),
    )

    def __init__(
        self,
        connection: aio_pika.AbstractConnection,
        queue_name: str,
        binds: Sequence[tuple[types.Exchange, str]],
        middleware_stack: Sequence[protocol.ConsumerMiddleware[_Proto]] | None = None,
        queue_arguments: common.Arguments | None = None,
    ):
        self._binds = binds
        self._connection = connection
        self._middleware_stack = cast(
            list[protocol.ConsumerMiddleware[_Proto]],
            list(
                reversed(
                    [
                        *self._default_middlewares,
                        *(middleware_stack or []),
                    ],
                ),
            ),
        )
        self._logger = stdout.get_logger()
        self._queue_name = queue_name
        self._queue_arguments = queue_arguments

    async def consume(self, callback: protocol.ConsumerFunc[_Proto]) -> None:
        async with self._connection.channel() as channel:
            await channel.set_qos(
                prefetch_count=((os.cpu_count() or 1) * 2) + 1,
            )

            queue = await channel.declare_queue(
                name=self._queue_name,
                durable=True,
                arguments=self._queue_arguments,
            )

            for exchange, routing_key in self._binds:
                declared_exchange = await channel.declare_exchange(
                    name=exchange.name,
                    type=exchange.type_,
                    durable=True,
                )

                await queue.bind(declared_exchange, routing_key)

            await self._consume(queue, callback)

    async def _consume(
        self,
        queue: aio_pika.AbstractQueue,
        callback: protocol.ConsumerFunc[_Proto],
    ) -> None:
        async def wrapper(incoming: aio_pika.AbstractIncomingMessage) -> None:
            msg = types.Message[_Proto](incoming, self._queue_name)

            try:
                await self._process(msg, callback)
            except Exception:
                self._logger.exception(
                    "An error occurred while processing message",
                    type=msg.body.DESCRIPTOR.full_name,
                )
            else:
                self._logger.info(
                    "Message processed.",
                    type=msg.body.DESCRIPTOR.full_name,
                )

        await queue.consume(wrapper)
        await asyncio.Future()

    async def _process(
        self,
        msg: types.Message[_Proto],
        callback: protocol.ConsumerFunc[_Proto],
    ) -> None:
        def factory(
            middleware_func: protocol.ConsumerMiddleware[_Proto],
            inner_func: protocol.ConsumerFunc[_Proto],
        ) -> protocol.ConsumerFunc[_Proto]:
            async def decorator(message_obj: types.Message[_Proto]) -> None:
                return await middleware_func(message_obj, inner_func)

            return decorator

        func = callback
        for middleware in self._middleware_stack:
            func = factory(middleware, func)

        await func(msg)
