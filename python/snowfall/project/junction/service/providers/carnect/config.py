import datetime

import pydantic

from snowfall.project.junction.provider import service
from snowfall.stdlib.service import application

_DEFAULT_TTL_IN_MINUTES = 45
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30
_RESERVATION_TIMEOUT_IN_SECONDS = 130


class CarnectConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_username: str
    api_password: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    env_name: str = "local"

    @property
    def is_test(self) -> bool:
        return self.env_name.lower() != "production"


class PricingSettings(application.Settings, CarnectConfig):
    amqp_dsn: pydantic.AmqpDsn
    provider_company_id: str
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)


class Settings(CarnectConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    storage_dsn: service.AnyDsn


class OrderSettings(application.Settings, CarnectConfig):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(
        seconds=_RESERVATION_TIMEOUT_IN_SECONDS,
    )
    storage_dsn: service.AnyDsn
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
