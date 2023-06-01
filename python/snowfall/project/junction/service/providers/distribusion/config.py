import datetime
from typing import Sequence

import pydantic

from snowfall.project.junction.provider import service

DEFAULT_TTL_IN_MINUTES = 45


class DistribusionConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: int = 500
    retailer_partner_number: str


class Settings(service.ProviderSettings, DistribusionConfig):
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)


class OrdersSettings(DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    send_customer_email: bool = True


class PricingSettings(DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=DEFAULT_TTL_IN_MINUTES)
    provider_company_id: str
