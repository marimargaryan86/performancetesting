from typing import NoReturn

from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.transport.grpc import rich_status


async def get_auth_token(context: aio.ServicerContext) -> str | NoReturn:
    # This does not actually return a Metadata class, but instead a tuple of tuples.
    # See https://github.com/grpc/grpc/issues/26498
    metadata = context.invocation_metadata()

    if not metadata:
        await _abort(context)

    for metadata_key, metadata_value in metadata:
        if metadata_key == "authentication":
            return metadata_value

    await _abort(context)


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
