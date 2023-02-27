from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.transport.grpc import rich_status


async def get_auth_token(context: aio.ServicerContext) -> str:
    metadata = dict(context.invocation_metadata())
    auth_token = metadata.get("authentication", None)
    if auth_token is None:
        await rich_status.abort_with_rich_status(
            context,
            rich_status.build_rich_status(
                code=StatusCode.UNAUTHENTICATED,
                error=error_details_pb2.BadRequest(
                    field_violations=[
                        error_details_pb2.BadRequest.FieldViolation(
                            field="AUTH Token",
                            description="Authentication token not found",
                        ),
                    ],
                ),
                description="Authentication token not found",
            ),
        )
    return auth_token
