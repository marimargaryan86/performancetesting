from google.protobuf import message
from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.transport.grpc import interceptor, rich_status


class ErrorHandlerServerInterceptor(interceptor.ServerInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: message.Message,
        context: aio.ServicerContext,
    ) -> message.Message:
        try:
            return await continuation(request, context)
        except cursor.CursorError as err:
            await rich_status.abort_with_rich_status(
                context=context,
                code=StatusCode.INVALID_ARGUMENT,
                error=error_details_pb2.BadRequest(
                    field_violations=[
                        error_details_pb2.BadRequest.FieldViolation(
                            field="page_token",
                            description=str(err),
                        ),
                    ],
                ),
                description="Invalid cursor",
            )
