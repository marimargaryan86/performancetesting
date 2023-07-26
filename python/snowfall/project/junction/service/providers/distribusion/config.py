import datetime
from collections.abc import Sequence

import pydantic

from snowfall.project.junction.provider import service
from snowfall.vendor.rate_limiter.config import RateLimitConfig

DEFAULT_TTL_IN_MINUTES = 45


class DistribusionConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: int = 500
    retailer_partner_number: str
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, RateLimitConfig]


class Settings(service.ProviderSettings, DistribusionConfig):
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    storage_dsn: service.AnyDsn


class OrdersSettings(service.Settings, DistribusionConfig):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    send_customer_email: bool = True
    storage_dsn: service.AnyDsn


class PricingSettings(DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    provider_company_id: str
