from typing import Literal, TypedDict

from pydantic import BaseModel

from snowfall.vendor.rate_limiter.gubernator_pb2 import Algorithm, Behavior

durations_mapping: dict[str, int] = {
    "calendar_minute": 0,
    "calendar_hour": 1,
    "calendar_day": 2,
    "calendar_week": 3,
    "calendar_month": 4,
    "calendar_year": 5,
}

_CalenderType = Literal[
    "calendar_minute",
    "calendar_hour",
    "calendar_day",
    "calendar_week",
    "calendar_month",
    "calendar_year",
]


class RateLimitConfig(BaseModel):
    name: str
    limit: int
    duration_s: int | _CalenderType
    algorithm: Literal["token", "leaky"]


class RateLimitConfigsApi(TypedDict):
    name: str
    limit: int
    duration: int
    algorithm: Algorithm
    behavior: Behavior
