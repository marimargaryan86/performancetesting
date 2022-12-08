import datetime
from typing import Sequence

import pydantic

from snowfall.stdlib import service

_DEFAULT_TTL_IN_MINUTES = 45


class DuffelConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_version: str = "v1"
    http_timeout: int = 30


class SearchesSettings(DuffelConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
