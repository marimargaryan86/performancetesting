import grpc
from google.protobuf import message

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.transport.grpc import interceptor, rich_status


class ErrorHandlerServerInterceptor(interceptor.ServerInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: message.Message,
        context: grpc.aio.ServicerContext,
    ) -> message.Message:
        try:
            return await continuation(request, context)
        except cursor.CursorError as err:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="page_token",
                    field_description=str(err),
                    description="Invalid cursor",
                ),
            )
