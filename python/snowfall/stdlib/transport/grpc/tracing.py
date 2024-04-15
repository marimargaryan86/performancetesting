import contextlib
from collections.abc import Callable, Iterator

from google.protobuf.message import Message
from grpc import StatusCode, aio
from sentry_sdk import Hub, tracing

from snowfall.stdlib.instrumentation.sentry import get_span
from snowfall.stdlib.transport.grpc import interceptor

_SPAN_CLIENT_OP = "grpc"
_SPAN_SERVER_OP = "grpc.server"


class TracingClientInterceptor(aio.UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> aio.UnaryUnaryCall | Message:
        with get_span(_SPAN_CLIENT_OP, client_call_details.method) as span:
            for header_key, header_value in span.iter_headers():
                client_call_details.metadata.add(header_key, header_value)

            return await continuation(
                client_call_details,
                request,
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
        transaction = tracing.Transaction.continue_from_headers(
            dict(context.invocation_metadata()),
            op=_SPAN_SERVER_OP,
            name=name,
            description=name,
        )

        with Hub(Hub.current).start_transaction(transaction) as span:
            span.set_status("ok")

            try:
                yield span
            finally:
                span.set_status(
                    (context.code() or StatusCode.OK).name.lower(),
                )
