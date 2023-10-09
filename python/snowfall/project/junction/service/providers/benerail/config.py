import base64
import datetime
import tempfile

import pydantic

from snowfall.project.junction.provider import service

_DEFAULT_API_TIMEOUT_IN_SECONDS = 50
_DEFAULT_TTL_IN_MINUTES = 45


def cert_tmp_path(cert_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(cert_base64))

        return tmp_file.name


class BenerailSettings(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    subscription_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    cert_base64: str


class DumpStationsSettings(BenerailSettings, service.Settings):
    geodata_address: str
    output_dir: pydantic.DirectoryPath = "."  # type: ignore[assignment]


class Settings(BenerailSettings, service.ProviderSettings):
    mongo_dsn: tuple[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    storage_dsn: service.AnyDsn


class PriceQuoteSettings(BenerailSettings, service.Settings):
    redis_dsn: pydantic.AnyUrl
    amqp_dsn: pydantic.AmqpDsn
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    provider_company_id: str


class OrdersSettings(BenerailSettings, service.Settings):
    redis_dsn: pydantic.AnyUrl
    amqp_dsn: pydantic.AmqpDsn
    storage_dsn: service.AnyDsn


class NotificationsSettings(BenerailSettings, service.Settings):
    amqp_dsn: pydantic.AmqpDsn
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
