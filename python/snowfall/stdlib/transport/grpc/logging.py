import contextlib
from collections.abc import AsyncIterator

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
        async with self._log(continuation.__name__, context, request):
            return await continuation(request, context)

    @contextlib.asynccontextmanager
    async def _log(
        self,
        name: str,
        context: aio.ServicerContext,
        request: Message,
    ) -> AsyncIterator[None]:
        try:
            yield
        except Exception as err:
            if isinstance(err, aio.BaseError):
                raise

            self._logger.exception(
                "An unhandled exception was raised in the gRPC server",
            )

            await context.abort(StatusCode.INTERNAL)
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
                response_size=request.ByteSize(),
            )
