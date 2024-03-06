import dataclasses
import datetime
import pathlib
from collections.abc import Mapping
from typing import TypeVar

import httpx

from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application

_DefaultTimeout = 5
_Settings = TypeVar("_Settings", bound=application.Settings)


@dataclasses.dataclass(frozen=True)
class Certificate(object):
    certificate_file: pathlib.Path
    key_file: pathlib.Path | None = None
    password: str | None = None

    def to_httpx_argument(self) -> str | tuple[str, str] | tuple[str, str | None, str]:
        if self.password:
            return (
                str(self.certificate_file),
                str(self.key_file) if self.key_file else None,
                self.password,
            )

        if self.key_file:
            return str(self.certificate_file), str(self.key_file)

        return str(self.certificate_file)


async def make_client(
    app: application.Application[_Settings],
    *,
    base_url: httpx.URL | None = None,
    follow_redirects: bool = False,
    headers: Mapping[str, str] | None = None,
    timeout: datetime.timedelta | None = None,
    cert: Certificate | None = None,
) -> httpx.AsyncClient:
    client = httpx.AsyncClient(
        base_url=base_url or "",
        follow_redirects=follow_redirects,
        headers=headers,
        timeout=(
            timeout.total_seconds()
            if timeout
            else datetime.timedelta(seconds=_DefaultTimeout).total_seconds()
        ),
        cert=cert.to_httpx_argument() if cert else None,
    )

    metrics.register(client)

    return await app.stack.enter_async_context(client)
