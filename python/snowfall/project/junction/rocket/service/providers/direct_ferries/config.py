import datetime

import pydantic

from snowfall.project.junction.rocket.provider import service

_API_TIMEOUT_DEFAULT_SECONDS = 40
_OFFER_TTL_DEFAULT_MINUTES = 45


class DfBaseSettings(service.Settings):
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_API_TIMEOUT_DEFAULT_SECONDS,
    )
    pay_company_id: str


class Settings(DfBaseSettings, service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=_OFFER_TTL_DEFAULT_MINUTES)
    storage_dsn: service.AnyDsn
