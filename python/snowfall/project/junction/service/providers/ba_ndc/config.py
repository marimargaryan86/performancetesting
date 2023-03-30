from typing import Sequence

import pydantic

from snowfall.project.junction.provider import service

_DEFAULT_TTL_IN_MINUTES = 45


class BaNdcConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    http_timeout: int = 30


class OffersSettings(service.OffersSettings, BaNdcConfig):
    amqp_dsn: pydantic.AnyUrl
    provider_company_id: str
    redis_dsn: pydantic.AnyUrl


class PricingSettings(BaNdcConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
