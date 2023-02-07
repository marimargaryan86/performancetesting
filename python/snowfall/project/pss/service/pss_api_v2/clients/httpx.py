from typing import AsyncGenerator

import httpx
from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings


async def get_proxy_async_httpx_client(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=settings.pss_v1_dsn) as client:
        yield client
