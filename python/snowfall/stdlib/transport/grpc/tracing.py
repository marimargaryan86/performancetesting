import contextlib
from typing import AsyncIterable, Callable, Iterator, Union

from google.protobuf.message import Message
from grpc import aio
from sentry_sdk import Hub, tracing

from snowfall.stdlib.instrumentation.sentry import get_span
from snowfall.stdlib.transport.grpc import interceptor

_SPAN_CLIENT_OP = "grpc"
_SPAN_SERVER_OP = "grpc.server"
_IterMsg = AsyncIterable[Message]


class TracingClientInterceptor(  # noqa: WPS215 (too many base classes)
    aio.UnaryUnaryClientInterceptor,
    aio.UnaryStreamClientInterceptor,
    aio.StreamUnaryClientInterceptor,
    aio.StreamStreamClientInterceptor,
):
    async def intercept_unary_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> Union[aio.UnaryUnaryCall, Message]:
        with get_span(_SPAN_CLIENT_OP, client_call_details.method) as span:
            for header_key, header_value in span.iter_headers():
                client_call_details.metadata.add(header_key, header_value)

            return await continuation(
                client_call_details,
                request,
            )

    async def intercept_unary_stream(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryStreamCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> Union[aio.UnaryStreamCall, _IterMsg]:
        with get_span(_SPAN_CLIENT_OP, client_call_details.method) as span:
            for header_key, header_value in span.iter_headers():
                client_call_details.metadata.add(header_key, header_value)

            return continuation(
                client_call_details,
                request,
            )

    async def intercept_stream_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, _IterMsg], aio.StreamUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request_iterator: _IterMsg,
    ) -> Union[aio.StreamUnaryCall, Message]:
        with get_span(_SPAN_CLIENT_OP, client_call_details.method) as span:
            for header_key, header_value in span.iter_headers():
                client_call_details.metadata.add(header_key, header_value)

            return await continuation(
                client_call_details,
                request_iterator,
            )

    async def intercept_stream_stream(
        self,
        continuation: Callable[[aio.ClientCallDetails, _IterMsg], aio.StreamStreamCall],
        client_call_details: aio.ClientCallDetails,
        request_iterator: _IterMsg,
    ) -> Union[aio.StreamStreamCall, _IterMsg]:
        with get_span(_SPAN_CLIENT_OP, client_call_details.method) as span:
            for header_key, header_value in span.iter_headers():
                client_call_details.metadata.add(header_key, header_value)

            return continuation(
                client_call_details,
                request_iterator,
            )


class TracingServerInterceptor(interceptor.ServerInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: Message,
        context: aio.ServicerContext,
    ) -> Message:
        with self._get_span(
            continuation.__name__,
            context,
        ):
            return await continuation(request, context)

    @contextlib.contextmanager
    def _get_span(
        self,
        name: str,
        context: aio.ServicerContext,
    ) -> Iterator[tracing.Span]:
        hub = Hub(Hub.current)
        transaction = tracing.Transaction.continue_from_headers(
            {
                metadata_key: metadata_value
                for metadata_key, metadata_value in context.invocation_metadata()
            },
            op=_SPAN_SERVER_OP,
            name=name,
        )

        with hub.start_transaction(transaction) as span:
            span.set_status("ok")

            try:
                yield span
            finally:
                if context.code():
                    span.set_status(context.code().value[1].replace(" ", "_"))
