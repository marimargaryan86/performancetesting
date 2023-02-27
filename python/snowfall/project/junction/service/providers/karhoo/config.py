import datetime
from typing import Sequence

import pydantic

from snowfall.stdlib import service

_DEFAULT_TTL_IN_MINUTES = 10
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class KarhooConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )


class OfferSettings(service.Settings, KarhooConfig):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    polling_wait_time_seconds: int
    polling_retries_attempts: int


class OrderSettings(service.Settings, KarhooConfig):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
