from __future__ import annotations

import asyncio
import os
from collections.abc import Sequence
from typing import TypeVar, cast

from aio_pika import abc
from google.protobuf import message
from pamqp import common

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import middlewares, protocol, types

_Proto = TypeVar("_Proto", bound=message.Message)


class Consumer(protocol.Consumer[_Proto]):
    _default_middlewares = [
        middlewares.with_sentry_context,
        middlewares.count_messages,
        middlewares.observe_wait_time,
        middlewares.observe_processing_time,
        middlewares.auto_ack_and_nack_factory(),
    ]

    def __init__(  # noqa: WPS211
        self,
        connection: abc.AbstractConnection,
        queue_name: str,
        binds: Sequence[tuple[types.Exchange, str]],
        middleware_stack: Sequence[protocol.ConsumerMiddleware[_Proto]] | None = None,
        queue_arguments: common.Arguments | None = None,
    ):
        self._binds = binds
        self._connection = connection
        self._middleware_stack = cast(
            list[protocol.ConsumerMiddleware[_Proto]],
            [
                *reversed(self._default_middlewares),
                *reversed(middleware_stack or []),
            ],
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
        queue: abc.AbstractQueue,
        callback: protocol.ConsumerFunc[_Proto],
    ) -> None:
        async def wrapper(incoming: abc.AbstractIncomingMessage) -> None:
            msg = types.Message[_Proto](incoming, self._queue_name)

            try:
                await self._process(msg, callback)
            except Exception:  # noqa: PIE786
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
