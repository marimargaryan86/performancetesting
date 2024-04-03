import datetime
from collections.abc import Sequence
from typing import Any

import pydantic

from snowfall.stdlib.integration.starlette import application as starlette

DEFAULT_GRPC_TIMEOUT = 45


class Settings(starlette.Settings):
    authentication_address: str
    searches_address: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    j_one_api_key: str
    reseller_j1_credentials_mapping: dict[str, Any]
    j_one_api_base_url: str
    mongo_dsn: Sequence[pydantic.AnyUrl]
    grpc_timeout: datetime.timedelta = datetime.timedelta(seconds=DEFAULT_GRPC_TIMEOUT)
    reseller_pay_companies: dict[str, str]
