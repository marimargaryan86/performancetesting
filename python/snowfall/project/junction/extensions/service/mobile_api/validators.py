import functools
import json
from typing import Awaitable, Callable, ParamSpec, TypeVar, cast

from starlette import requests, status

from snowfall.project.junction.extensions.service.mobile_api import repository
from snowfall.project.junction.extensions.service.mobile_api.models.cached_rate import (
    CachedRate,
)
from snowfall.stdlib.integration.starlette import models, request_helpers

_In = ParamSpec("_In")
_Out = TypeVar("_Out")


def voucher_validator(
    func: Callable[_In, Awaitable[_Out]],
) -> Callable[_In, Awaitable[_Out | models.JsonApiResponse]]:
    @functools.wraps(func)
    async def wrapper(
        *args: _In.args,
        **kwargs: _In.kwargs,
    ) -> _Out | models.JsonApiResponse:
        body = await request_helpers.flatten_request(args[1])  # type: ignore[arg-type]
        voucher_code = body.get("voucher", "")
        voucher = None
        if voucher_code:
            vouchers_repository = cast(
                repository.VouchersRepository,
                kwargs["vouchers_repository"],
            )
            voucher = await vouchers_repository.find_valid_voucher(
                voucher_code,
            )
            if not voucher:
                return models.JsonApiResponse(
                    models.Body(
                        errors=[
                            models.Error(
                                status=str(status.HTTP_400_BAD_REQUEST),
                                code="invalid_voucher",
                                detail="Invalid voucher",
                                source=models.ErrorSourcePointer(
                                    pointer="/data/relationships/voucher",
                                ),
                            ),
                        ],
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        kwargs["voucher"] = voucher
        return await func(*args, **kwargs)

    return wrapper


def get_session_token_rates(
    func: Callable[_In, Awaitable[_Out]],
) -> Callable[_In, Awaitable[_Out | models.JsonApiResponse]]:
    @functools.wraps(func)
    async def wrapper(
        *args: _In.args,
        **kwargs: _In.kwargs,
    ) -> _Out | models.JsonApiResponse:
        offers_rates_repository = cast(
            repository.OffersRatesRepository,
            kwargs["offers_rates_repository"],
        )
        request = cast(requests.Request, args[1])
        cached_rate = await offers_rates_repository.get(
            request.headers.get("Session-Token", ""),
        )
        kwargs["cached_rate"] = cached_rate
        if cached_rate:
            kwargs["cached_rate"] = CachedRate(**json.loads(cached_rate))
        return await func(*args, **kwargs)

    return wrapper
