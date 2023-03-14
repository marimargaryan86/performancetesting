import abc
import functools
from typing import Awaitable, Callable, Optional

from google.protobuf import message
from grpc import HandlerCallDetails, RpcMethodHandler, aio, experimental

Continuation = Callable[[HandlerCallDetails], Awaitable[Optional[RpcMethodHandler]]]
UnaryUnary = Callable[
    [message.Message, aio.ServicerContext],
    Awaitable[message.Message],
]


class ServerInterceptor(abc.ABC, aio.ServerInterceptor):
    @abc.abstractmethod
    async def intercept_unary_unary(
        self,
        continuation: UnaryUnary,
        request: message.Message,
        context: aio.ServicerContext,
    ) -> message.Message:
        """Intercept unary to unary communication."""

    async def intercept_service(
        self,
        continuation: Continuation,
        handler_call_details: HandlerCallDetails,
    ) -> RpcMethodHandler | None:
        method_handler = await continuation(handler_call_details)

        if not method_handler or not method_handler.unary_unary:
            return method_handler

        def wrapper(func: UnaryUnary) -> UnaryUnary:
            @functools.wraps(func)
            async def decorator(
                request: message.Message,
                context: aio.ServicerContext,
            ) -> message.Message:
                return await self.intercept_unary_unary(func, request, context)

            return decorator

        return experimental.wrap_server_method_handler(
            wrapper,
            method_handler,
        )
