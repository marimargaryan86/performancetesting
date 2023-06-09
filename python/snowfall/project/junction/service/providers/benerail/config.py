import datetime

import pydantic

from snowfall.stdlib import service

_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class DumpStationsSettings(service.Settings):
    geodata_address: str
    api_base_url: pydantic.AnyUrl
    subscription_key: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    cert_path: pydantic.FilePath
    private_key_path: pydantic.FilePath
    output_dir: pydantic.DirectoryPath = "."  # type: ignore[assignment]
    private_key_password: str | None = None
