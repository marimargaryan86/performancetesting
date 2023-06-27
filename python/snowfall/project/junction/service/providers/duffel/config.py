import datetime
from collections.abc import Sequence
from typing import Any

import pydantic

from snowfall.project.junction.provider import service
from snowfall.vendor.rate_limiter.config import RateLimitConfig

DEFAULT_TTL_IN_MINUTES = 45


class DuffelConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_version: str = "v1"
    http_timeout: int = 30
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]
    resellers_map: dict[str, dict[str, Any]] = {}


class Settings(DuffelConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    enabled_airlines: set[str] = pydantic.Field(default_factory=set)
    disabled_airlines: set[str] = pydantic.Field(default_factory=set)


class PricingSettings(DuffelConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    provider_company_id: str
