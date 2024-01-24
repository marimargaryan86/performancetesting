import functools
import time
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import ParamSpec, TypeVar

from asyncstdlib import functools as async_functools

_In = ParamSpec("_In")
_Out = TypeVar("_Out")


def async_cache_ttl(
    ttl: timedelta | None = None,
    maxsize: int = 128,
    typed: bool = False,  # noqa: FBT001,FBT002
) -> Callable[[Callable[_In, Awaitable[_Out]]], Callable[_In, Awaitable[_Out]]]:
    def decorator(
        fn: Callable[_In, Awaitable[_Out]],
    ) -> Callable[_In, Awaitable[_Out]]:
        @async_functools.lru_cache(maxsize=maxsize, typed=typed)
        def cached(  # noqa: WPS430
            *args: _In.args,
            time_salt: int,
            **kwargs: _In.kwargs,
        ) -> Awaitable[_Out]:
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        async def wrapper(*args: _In.args, **kwargs: _In.kwargs) -> _Out:
            return await cached(
                *args,
                **kwargs,
                time_salt=int(time.time() / ttl.total_seconds()) if ttl else 0,
            )

        return wrapper

    return decorator
