import contextlib
from typing import Iterator

from google.protobuf.message import Message
from grpc import StatusCode, aio
from grpc_status import rpc_status

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc import interceptor


class LoggingServerInterceptor(interceptor.ServerInterceptor):
    _logger = stdout.get_logger()

    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: Message,
        context: aio.ServicerContext,
    ) -> Message:
        with self._log(continuation.__name__, context):
            return await continuation(request, context)

    @contextlib.contextmanager
    def _log(
        self,
        name: str,
        context: aio.ServicerContext,
    ) -> Iterator[None]:
        try:
            yield
        finally:
            status = (
                rpc_status.code_to_grpc_status_code(context.code())
                if context.code()
                else StatusCode.OK
            )

            self._logger.info(
                "Request processed.",
                name=name,
                status=status.value[1].replace(" ", "_"),
            )
