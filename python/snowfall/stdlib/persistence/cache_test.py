from datetime import timedelta
from unittest import mock

import freezegun

from snowfall.stdlib.persistence.cache import async_cache_ttl


async def async_function(param: int) -> int:
    return param


class TestCache:
    async def test_cache(self) -> None:
        async_function_mock = mock.AsyncMock(wraps=async_function)
        decorated_async_function = async_cache_ttl()(async_function_mock)

        result1 = await decorated_async_function(1)
        result2 = await decorated_async_function(1)
        assert result1 == result2
        async_function_mock.assert_called_once()

    async def test_cache_with_different_params(self) -> None:
        async_function_mock = mock.AsyncMock(wraps=async_function)
        decorated_async_function = async_cache_ttl()(async_function_mock)

        result1 = await decorated_async_function(1)
        result2 = await decorated_async_function(2)
        assert result1 != result2
        assert async_function_mock.call_count == 2

    async def test_cache_with_ttl(self) -> None:
        async_function_mock = mock.AsyncMock(wraps=async_function)
        decorated_async_function = async_cache_ttl(ttl=timedelta(seconds=2))(
            async_function_mock,
        )

        with freezegun.freeze_time() as frozen_datetime:
            await decorated_async_function(1)
            await decorated_async_function(1)
            frozen_datetime.tick(timedelta(seconds=3))
            await decorated_async_function(1)
            assert async_function_mock.call_count == 2
