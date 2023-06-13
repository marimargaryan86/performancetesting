import contextlib
import contextvars
from typing import Any, Callable, Iterator, NoReturn

import jwt
from google.protobuf.message import Message
from google.rpc import error_details_pb2
from grpc import StatusCode, aio

from snowfall.stdlib.transport.grpc import rich_status

_AUTH_CONTEXT: contextvars.ContextVar[str] = contextvars.ContextVar("auth")
_AUTH_METADATA_KEY = "authentication"


class MetadataContextClientInterceptor(aio.UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> aio.UnaryUnaryCall | Message:
        with contextlib.suppress(LookupError):
            client_call_details.metadata.add(_AUTH_METADATA_KEY, _AUTH_CONTEXT.get())

        return await continuation(
            client_call_details,
            request,
        )


@contextlib.contextmanager
def auth_context(authentication: str) -> Iterator[None]:
    token = _AUTH_CONTEXT.set(authentication)

    try:
        yield
    finally:
        _AUTH_CONTEXT.reset(token)


async def get_auth_token(context: aio.ServicerContext) -> dict[str, Any]:
    # This does not actually return a Metadata class, but instead a tuple of tuples.
    # See https://github.com/grpc/grpc/issues/26498
    metadata = context.invocation_metadata()

    if not metadata:
        await _abort(context, "Authentication token not found")

    for metadata_key, metadata_value in metadata:
        if metadata_key == _AUTH_METADATA_KEY:
            try:
                return jwt.decode(
                    metadata_value,
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )
            except jwt.exceptions.PyJWTError:
                await _abort(context, "Authentication token invalid")

    return await _abort(context, "Authentication token not found")


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
