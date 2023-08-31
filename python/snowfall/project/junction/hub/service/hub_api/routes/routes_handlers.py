import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import grpc
from starlette import requests, status

from snowfall.project.junction.go.adapter import errors
from snowfall.stdlib.integration.starlette import messages, models
from snowfall.stdlib.transport.grpc import rich_status

_In = ParamSpec("_In")
_Out = TypeVar("_Out")


async def _handle_invalid_argument(
    err: grpc.aio.AioRpcError,
    request: requests.Request,
) -> models.JsonApiResponse:
    field_to_source = {
        "account_id": models.ErrorSourcePointer(
            pointer="/data/relationships/account/data/id",
        ),
        "currency": models.ErrorSourcePointer(
            pointer="/data/relationships/currency/data/id",
        ),
        "transaction": models.ErrorSourcePointer(
            pointer="/data/relationships/transaction/data/id",
        ),
        "refundedUs": models.ErrorSourcePointer(
            pointer="/data/attributes/currency",
        ),
    }
    rich_error = list(rich_status.iter_rich_statuses(err))
    if not rich_error:
        raise errors.NotFoundError(  # noqa: WPS220
            err.details(),
        ) from err
    grpc_error = rich_error[0].field_violations[0]  # type: ignore[attr-defined]
    if grpc_error.field not in field_to_source:
        raise errors.UnhandledError(
            grpc_error.description,
        ) from err
    error = models.Error(
        status=str(status.HTTP_404_NOT_FOUND),
        code="not_found",
        detail=grpc_error.description,
        source=field_to_source[grpc_error.field],
    )
    return await messages.create_response(
        body=models.Body(
            errors=[error],
        ),
        request=request,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def grpc_errors_handler(
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
            match err.code():
                case grpc.StatusCode.INVALID_ARGUMENT:
                    return await _handle_invalid_argument(
                        err,
                        args[1],  # type: ignore[arg-type]
                    )
                case grpc.StatusCode.NOT_FOUND:
                    raise errors.NotFoundError(
                        err.details(),
                    ) from err

            raise errors.UnhandledError(
                err.details(),
            ) from err

    return wrapper
