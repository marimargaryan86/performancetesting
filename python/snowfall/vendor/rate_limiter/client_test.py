import asyncio
import time
from unittest import mock

import pytest

from snowfall.vendor.rate_limiter.client import SECOND
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient
from snowfall.vendor.rate_limiter.config import RateLimitConfig
from snowfall.vendor.rate_limiter.gubernator_pb2 import GetRateLimitsResp

config = RateLimitConfig(
    name="test",
    limit=120,
    duration_s="calendar_minute",
    algorithm="token",
)


def create_response(status: str, offset: float = 10) -> GetRateLimitsResp:
    return GetRateLimitsResp(
        responses=[
            {
                "metadata": {},
                "status": status,
                "limit": 1,
                "remaining": 0,
                "reset_time": int(time.time() * SECOND + offset * SECOND),  # ms
                "error": "",
            },
        ],
    )


async def test_rates_limit_was_under_limit() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = lambda _: create_response("UNDER_LIMIT")

        await client.rate_limit(60)


async def test_rates_limit_was_over_limit() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    first_resp = create_response("OVER_LIMIT", 1)
    second_resp = create_response("UNDER_LIMIT")
    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = iter((first_resp, second_resp))

        async with asyncio.timeout(2):  # Ensure failing test doesn't hang.
            await client.rate_limit(60)


async def test_rates_limit_raises_an_exception() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = lambda _: create_response("OVER_LIMIT")

        async with asyncio.timeout(2):
            with pytest.raises(TimeoutError):
                await client.rate_limit(1)


async def test_rate_limit_raises_smaller_reset(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = RateLimitClient("dummy_host:1111", config)
    sleep = asyncio.sleep

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = lambda _: create_response("OVER_LIMIT", 0.4)

        target = "snowfall.vendor.rate_limiter.client.asyncio.sleep"
        with mock.patch(target, autospec=True, spec_set=True) as sleep_mock:
            sleep_mock.side_effect = sleep
            async with asyncio.timeout(2):
                with pytest.raises(TimeoutError):
                    await client.rate_limit(1)
            assert sleep_mock.call_count == 2


async def test_rate_limit_no_timeout(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = lambda _: create_response("OVER_LIMIT")

        target = "snowfall.vendor.rate_limiter.client.asyncio.sleep"
        with mock.patch(target, autospec=True, spec_set=True) as sleep_mock:
            async with asyncio.timeout(1):
                with pytest.raises(TimeoutError):
                    await client.rate_limit()
            sleep_mock.assert_not_called()
