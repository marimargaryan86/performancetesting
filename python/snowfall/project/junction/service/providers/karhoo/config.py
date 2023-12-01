import datetime

import pydantic

from snowfall.project.junction.provider import service
from snowfall.stdlib.service import application

_DEFAULT_TTL_IN_MINUTES = 45
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class KarhooConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )


class Settings(KarhooConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)


class OfferSettings(application.Settings, KarhooConfig):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    polling_wait_time_seconds: int = 10
    polling_retries_attempts: int = 4
    provider_company_id: str
    reseller_providers: dict[str, list[str]] = pydantic.Field(default_factory=dict)


class OrderSettings(application.Settings, KarhooConfig):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
