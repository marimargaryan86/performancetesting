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


def create_response(status: str) -> GetRateLimitsResp:
    return GetRateLimitsResp(
        responses=[
            {
                "metadata": {},
                "status": status,
                "limit": 1,
                "remaining": 0,
                "reset_time": int(time.time() * SECOND + 10 * SECOND),  # ms
                "error": "",
            },
        ],
    )


over_limit_response = create_response("OVER_LIMIT")
under_limit_response = create_response("UNDER_LIMIT")


async def test_rates_limit_was_under_limit() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.return_value = under_limit_response

        await client.rate_limit(60)


async def test_rates_limit_was_over_limit() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = (over_limit_response, under_limit_response)

        await client.rate_limit(60)


async def test_rates_limit_raises_an_exception() -> None:
    client = RateLimitClient("dummy_host:1111", config)

    with mock.patch.object(
        client._stub,  # noqa: WPS437
        "GetRateLimits",
        new=mock.AsyncMock(),
    ) as mock_obj:
        mock_obj.side_effect = lambda _: create_response("OVER_LIMIT")

        with pytest.raises(TimeoutError):
            await client.rate_limit(1)
