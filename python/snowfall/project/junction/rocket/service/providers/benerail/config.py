from __future__ import annotations

import datetime

import pydantic

from snowfall.project.junction.rocket.provider import service
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    DEFAULT_TTL_MINUTES,
)


class Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_MINUTES)
    storage_dsn: service.AnyDsn
    mongo_dsn: tuple[pydantic.AnyUrl]
    subscription_key: str
    api_base_url: pydantic.AnyUrl
    cert_base64: str
    pay_company_id: str


class OrdersSettings(service.ProviderSettings, service.Settings):
    redis_dsn: pydantic.RedisDsn
    amqp_dsn: pydantic.AmqpDsn
    storage_dsn: service.AnyDsn
    cert_base64: str
    subscription_key: str
    api_base_url: pydantic.AnyUrl
    use_mobile_tickets: bool = True


class PricingSettings(service.ProviderSettings):
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_MINUTES)
    cert_base64: str
    subscription_key: str
    api_base_url: pydantic.AnyUrl
    pay_company_id: str
