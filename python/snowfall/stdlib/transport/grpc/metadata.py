from typing import Any, NoReturn

import jwt
from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.transport.grpc import rich_status


async def get_auth_token(context: aio.ServicerContext) -> dict[str, Any]:
    # This does not actually return a Metadata class, but instead a tuple of tuples.
    # See https://github.com/grpc/grpc/issues/26498
    metadata = context.invocation_metadata()

    if not metadata:
        await _abort(context, "Authentication token not found")

    for metadata_key, metadata_value in metadata:
        if metadata_key == "authentication":
            try:
                return jwt.decode(
                    metadata_value,
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )
            except jwt.exceptions.PyJWTError:
                await _abort(context, "Authentication token invalid")

    await _abort(context, "Authentication token not found")


async def _abort(context: aio.ServicerContext, description: str) -> NoReturn:
    await rich_status.abort_with_rich_status(
        context,
        rich_status.build_rich_status(
            code=StatusCode.UNAUTHENTICATED,
            error=error_details_pb2.BadRequest(
                field_violations=[
                    error_details_pb2.BadRequest.FieldViolation(
                        field="AUTH Token",
                        description=description,
                    ),
                ],
            ),
            description=description,
        ),
    )
