from typing import NoReturn

from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.transport.grpc import rich_status


async def get_auth_token(context: aio.ServicerContext) -> str | NoReturn:
    metadata = context.invocation_metadata()

    if not metadata:
        await _abort(context)

    auth_token = metadata.get("authentication")

    if not auth_token:
        await _abort(context)

    return auth_token


async def _abort(context: aio.ServicerContext) -> NoReturn:
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
