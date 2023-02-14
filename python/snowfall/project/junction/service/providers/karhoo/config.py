import datetime
from typing import Sequence

import pydantic

from snowfall.stdlib import service

_DEFAULT_TTL_IN_MINUTES = 45
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class OfferSettings(service.Settings):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
