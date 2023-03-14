import datetime

import pydantic

from snowfall.stdlib import service


class DFSetting(service.Settings):
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(minutes=2)
    output_path: str = "dist/import/gtfs-feed/direct-ferries"
