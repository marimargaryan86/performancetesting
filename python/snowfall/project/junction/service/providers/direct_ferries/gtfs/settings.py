import pydantic

from snowfall.stdlib import service


class DFSetting(service.Settings):
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    timeout: int
    always_run: bool = False
    mongo_dsn: tuple[pydantic.AnyUrl]
    output_path: str = "dist/import/gtfs-feed/direct-ferries"
    redis_dsn: tuple[pydantic.AnyUrl]
