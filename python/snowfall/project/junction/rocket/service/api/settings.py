import datetime
from typing import Any

import pydantic

from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.service import application

DEFAULT_GRPC_TIMEOUT = 45
_DEFAULT_SUGGESTION_SEARCH_TTL_MINUTES = 30


class CommonSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    amqp_timeout: datetime.timedelta | None = None
    j_one_api_base_url: str
    j_one_api_key: str
    mongo_dsn: pydantic.MongoDsn
    places_address: str
    reseller_j1_credentials_mapping: dict[str, Any]
    searches_address: str
    suggestion_search_ttl: datetime.timedelta = datetime.timedelta(
        minutes=_DEFAULT_SUGGESTION_SEARCH_TTL_MINUTES,
    )


class Settings(starlette.Settings, CommonSettings):
    authentication_address: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    grpc_timeout: datetime.timedelta = datetime.timedelta(seconds=DEFAULT_GRPC_TIMEOUT)
    reseller_pay_companies: dict[str, str]
    reseller_currencies: dict[str, str]
    j_one_pay_company_id: str
    redis_dsn: pydantic.RedisDsn
