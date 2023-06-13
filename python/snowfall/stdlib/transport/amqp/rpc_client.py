from __future__ import annotations

import asyncio
from collections.abc import MutableMapping
from typing import Any, Generic, TypeVar

from aio_pika import Message, abc, connect
from google.protobuf import message

from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import types

_Proto = TypeVar("_Proto", bound=message.Message)


class RpcClient(Generic[_Proto]):
    _connection: abc.AbstractConnection
    _channel: abc.AbstractChannel
    _callback_queue: abc.AbstractQueue

    def __init__(
        self,
        address: str,
        producer_exchange: types.Exchange,
        routing_key: str,
        timeout: int | None = 5,
    ):
        self._address = address
        self._producer_exchange = producer_exchange
        self._routing_key = routing_key
        self._timeout = timeout
        self._futures: MutableMapping[str, asyncio.Future[Any]] = {}

        self._loop = asyncio.get_running_loop()

    async def connect(self) -> RpcClient[_Proto]:
        self._connection = await connect(
            self._address,
            loop=self._loop,
        )
        self._channel = await self._connection.channel()
        self._callback_queue = await self._channel.declare_queue(exclusive=True)
        await self._callback_queue.consume(self._on_response)
        return self

    async def call(self, request: Any) -> _Proto:
        correlation_id = string.uuid()
        future = self._loop.create_future()
        self._futures[correlation_id] = future
        declared_exchange = await self._channel.declare_exchange(
            name=self._producer_exchange.name,
            type=self._producer_exchange.type_,
            durable=True,
        )
        await declared_exchange.publish(
            Message(
                content_type="application/x-protobuf",
                body=protobuf.AnySerializer.serialize(request),
                correlation_id=correlation_id,
                reply_to=self._callback_queue.name,
            ),
            routing_key=self._routing_key,
        )
        return await asyncio.wait_for(
            future,
            timeout=float(self._timeout) if self._timeout else None,
        )

    async def _on_response(self, msg: abc.AbstractIncomingMessage) -> None:
        if msg.correlation_id is None:
            return
        future: asyncio.Future[Any] = self._futures.pop(msg.correlation_id)

        future.set_result(protobuf.AnySerializer[_Proto].deserialize(msg.body))
        await msg.ack()
