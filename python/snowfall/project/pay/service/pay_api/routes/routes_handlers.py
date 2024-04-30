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
    "payer_id": models.ErrorSourcePointer(
        pointer="/data/relationships/payer/data/id",
    ),
    "from_currency": models.ErrorSourcePointer(
        pointer="/data/relationships/fromCurrency/data/id",
    ),
    "to_currency": models.ErrorSourcePointer(
        pointer="/data/relationships/toCurrency/data/id",
    ),
    "quotation_id": models.ErrorSourcePointer(
        pointer="/data/relationships/quotation/data/id",
    ),
    "external_reference_id": models.ErrorSourcePointer(
        pointer="/data/attributes/externalReference",
    ),
}


async def _handle_invalid_argument(
    err: grpc.aio.AioRpcError,
    request: requests.Request,
) -> models.JsonApiResponse:
    rich_error = list(rich_status.iter_rich_statuses(err))
    if not rich_error:
        raise errors.NotFoundError(  # noqa: WPS220
            err.details(),
        ) from err
    grpc_error = rich_error[0].field_violations[0]  # type: ignore[attr-defined]
    source_value = field_to_source.get(grpc_error.field)
    if source_value is not None:
        error = models.Error(
            status=str(status.HTTP_400_BAD_REQUEST),
            code="bad_request",
            detail=grpc_error.description,
            source=source_value,
        )
        return await messages.create_response(
            body=models.Body(
                errors=[error],
            ),
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    raise errors.UnhandledError(
        grpc_error.description,
    ) from err


async def _handle_not_found(
    err: grpc.aio.AioRpcError,
    request: requests.Request,
) -> models.JsonApiResponse:
    trailing_metadata = err.trailing_metadata()
    if trailing_metadata:
        metadata = {field[0]: field[1] for field in trailing_metadata}

        source_value = field_to_source.get(metadata.get("field_name", "unknown"))
        if source_value is not None:
            error = models.Error(
                status=str(status.HTTP_404_NOT_FOUND),
                code="not_found",
                detail=metadata["field_description"],
                source=source_value,
            )
            return await messages.create_response(
                body=models.Body(
                    errors=[error],
                ),
                request=request,
                status_code=status.HTTP_404_NOT_FOUND,
            )

    raise errors.NotFoundError(
        err.details(),
    ) from err


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
                    return await _handle_not_found(
                        err,
                        args[1],  # type: ignore[arg-type]
                    )

            raise errors.UnhandledError(
                err.details(),
            ) from err

    return wrapper
