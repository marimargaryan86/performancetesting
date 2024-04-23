import datetime
from typing import Any

import pydantic

from snowfall.project.junction.provider import service
from snowfall.vendor.rate_limiter.config import RateLimitConfig

DEFAULT_TTL_IN_MINUTES = 45


class DuffelConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_version: str = "v1"
    http_timeout: datetime.timedelta = datetime.timedelta(seconds=30)  # noqa: WPS432
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]
    resellers_map: dict[str, dict[str, Any]] = pydantic.Field(default_factory=dict)


class Settings(DuffelConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    enabled_airlines: set[str] = pydantic.Field(default_factory=set)
    disabled_airlines: set[str] = pydantic.Field(default_factory=set)
    storage_dsn: service.AnyDsn


class PricingSettings(DuffelConfig, service.Settings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    provider_company_id: str
