import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import grpc
from google.protobuf import message
from google.rpc import error_details_pb2

from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.transport.grpc import rich_status

_In = ParamSpec("_In")
_Out = TypeVar("_Out")
Proto = TypeVar("Proto", bound=message.Message)


class CursorError(Exception):
    """Raised when a cursor is invalid."""


class NotFoundError(Exception):
    """Raised when a resource is not found."""


class ServiceUnavailableError(Exception):
    """Raised when a resource is not found."""


class UnhandledError(Exception):
    """Raised when an unhandled error occurs."""


class UnprocessableEntityError(Exception):
    """Raised when it is not possible to process the request due to rules failure."""


class ForbiddenError(Exception):
    """Raised when a user does not have access to execute the requested operation."""


def handle_grpc_errors(
    func: Callable[_In, Awaitable[_Out]],
) -> Callable[_In, Awaitable[_Out | models.JsonApiResponse]]:
    @functools.wraps(func)
    async def wrapper(
        *args: _In.args,
        **kwargs: _In.kwargs,
    ) -> _Out | models.JsonApiResponse:
        try:
            return await func(*args, **kwargs)
        except grpc.aio.AioRpcError as err:
            _handle_grpc_exception(err)

            match err.code():
                case grpc.StatusCode.NOT_FOUND:
                    raise NotFoundError(err.details()) from err
                case grpc.StatusCode.UNAVAILABLE:
                    raise ServiceUnavailableError(err.details()) from err

            raise UnhandledError(err.details()) from err

    return wrapper


def _handle_bad_request(
    status: error_details_pb2.BadRequest,
    err: grpc.aio.AioRpcError,
) -> None:
    for violation in status.field_violations:
        if violation.field == "page_token":
            raise CursorError(violation.description) from err


def _handle_unprocessable_entity(err: grpc.aio.AioRpcError) -> None:
    raise UnprocessableEntityError(err.details()) from err


def _handle_grpc_exception(err: grpc.aio.AioRpcError) -> None:
    for status in rich_status.iter_rich_statuses(err):
        if isinstance(status, error_details_pb2.BadRequest):
            _handle_bad_request(status, err)
        elif isinstance(status, error_details_pb2.PreconditionFailure):
            _handle_unprocessable_entity(err)
