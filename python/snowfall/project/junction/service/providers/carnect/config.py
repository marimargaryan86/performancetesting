import datetime

import pydantic

from snowfall.project.junction.provider import service
from snowfall.stdlib.service import application

_DEFAULT_TTL_IN_MINUTES = 45
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class CarnectConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_username: str
    api_password: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    use_carnect_in_test_mode: bool = True


class PricingSettings(application.Settings, CarnectConfig):
    amqp_dsn: pydantic.AmqpDsn


class Settings(CarnectConfig, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
