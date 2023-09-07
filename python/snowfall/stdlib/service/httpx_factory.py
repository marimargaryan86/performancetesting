import datetime
from collections.abc import Mapping
from typing import TypeVar

import httpx

from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application

_DefaultTimeout = 5
_Settings = TypeVar("_Settings", bound=application.Settings)


async def make_client(
    app: application.AsyncApplication[_Settings],
    *,
    base_url: httpx.URL | None = None,
    follow_redirects: bool = False,
    headers: Mapping[str, str] | None = None,
    timeout: datetime.timedelta | None = None,
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
    )

    metrics.register(client)

    return await app.stack.enter_async_context(client)
