import logging
from collections.abc import Mapping
from typing import Any

import allure
import httpx

from snowfall.project.junction.api_automation.service_objects.helper import (
    generate_curl_command,
)
from snowfall.vendor.junction.client import BaseClient

logger = logging.getLogger()

METHOD_GET = "GET"
METHOD_POST = "POST"


class ClientWrapper(BaseClient):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
        sentry_url: str | None = None,
    ):
        super().__init__(base_url=base_url, auth=auth, client=client)
        self._token = token
        self._sentry_url = sentry_url
        self._cookie_header = client.headers.get("Cookie") if client else None
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    async def request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        headers: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        curl_command = generate_curl_command(
            base_url=str(self._base_url),
            method=method,
            url=url,
            cookie_header=self._cookie_header,
            token=self._token,
            query_parameters=query_parameters,
            body=payload,
            headers=headers,
        )
        allure.attach(curl_command, "curl")

        return await self._make_request(
            method=method,
            url=url,
            query_parameters=query_parameters,
            headers=headers,
            payload=payload,
        )
