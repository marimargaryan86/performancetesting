import asyncio
import time
from types import TracebackType
from typing import Self

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.rate_limiter.config import (
    RateLimitConfig,
    RateLimitConfigsApi,
    durations_mapping,
)
from snowfall.vendor.rate_limiter.gubernator_pb2 import (
    Algorithm,
    Behavior,
    GetRateLimitsReq,
    RateLimitReq,
    RateLimitResp,
    Status,
)
from snowfall.vendor.rate_limiter.gubernator_pb2_grpc import V1Stub

SECOND = 1000


class Client(object):
    def __init__(
        self,
        grpc_host: str,
        config: RateLimitConfig,
    ):
        self._channel = create_channel(grpc_host)
        self._stub = V1Stub(self._channel)
        self._config: RateLimitConfigsApi
        self._logger = stdout.get_logger()

        if isinstance(config.duration_s, str):
            duration = durations_mapping[config.duration_s]
            behavior = Behavior.DURATION_IS_GREGORIAN
        else:
            duration = config.duration_s * SECOND
            behavior = Behavior.BATCHING

        if config.algorithm == "token":
            algorithm = Algorithm.TOKEN_BUCKET
        else:
            algorithm = Algorithm.LEAKY_BUCKET

        self._config = RateLimitConfigsApi(
            name=config.name,
            limit=config.limit,
            duration=duration,
            algorithm=algorithm,
            behavior=behavior,
        )

    async def __aenter__(self) -> Self:
        await self._channel.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._channel.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )

    async def rate_limit(self, timeout: float = 0, hits: int = 1) -> None:
        cutoff_time_ms = (time.time() + timeout) * SECOND

        limit = await self._get_rate_limits(hits)
        while limit.status != Status.UNDER_LIMIT:
            if limit.reset_time >= cutoff_time_ms:
                self._logger.warning(
                    "Timeout occurred for %s (%ss)",
                    self._config["name"],
                    timeout,
                )
                raise asyncio.TimeoutError()

            time_diff_s = (limit.reset_time / SECOND) - time.time()
            self._logger.info(
                "Rate limit was reached for %s (retry after %.1fs)",
                self._config["name"],
                time_diff_s,
            )
            await asyncio.sleep(time_diff_s)

            limit = await self._get_rate_limits(hits)

    async def _get_rate_limits(self, hits: int) -> RateLimitResp:
        rate_limit_req = RateLimitReq(hits=hits, unique_key="1", **self._config)
        get_rate_limits_req = GetRateLimitsReq(requests=[rate_limit_req])
        response = await self._stub.GetRateLimits(get_rate_limits_req)

        return response.responses[0]
