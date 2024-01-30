import datetime
import uuid

import pydantic

from snowfall.project.junction.content import bootstrap

PROVIDER_NAME = "Benerail"
PROVIDER_ID = uuid.UUID("caefde65-c15c-4b60-b8d9-27638b50b08f")

DEFAULT_API_TIMEOUT_IN_SECONDS = 50


class Settings(bootstrap.Settings):
    api_base_url: pydantic.AnyUrl
    subscription_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    cert_path: str
    mongo_dsn: tuple[pydantic.AnyUrl]
    should_retrieve_offers: bool = False
