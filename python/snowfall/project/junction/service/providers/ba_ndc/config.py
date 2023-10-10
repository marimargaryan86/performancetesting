import datetime

import pydantic

from snowfall.project.junction.provider import service
from snowfall.vendor.rate_limiter.config import RateLimitConfig

_DEFAULT_TTL_IN_MINUTES = 45


class BaNdcConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    http_timeout: int = 30


class Settings(BaNdcConfig, service.ProviderSettings):
    amqp_dsn: pydantic.AmqpDsn
    provider_company_id: str
    redis_dsn: pydantic.RedisDsn
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]
    storage_dsn: service.AnyDsn


class PricingSettings(BaNdcConfig, service.Settings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    provider_company_id: str
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
