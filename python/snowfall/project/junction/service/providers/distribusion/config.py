import datetime
from typing import Sequence

import pydantic

from snowfall.stdlib import service

_DEFAULT_TTL_IN_MINUTES = 45


class DistribusionConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: int = 500
    retailer_partner_number: str


class OrdersSettings(DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr


class SearchesSettings(DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
