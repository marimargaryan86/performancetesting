from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.vendor.duffel import client
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


class DuffelClientFactory(object):
    def __init__(  # noqa: WPS211
        self,
        api_base_url: str,
        api_key: str,
        version: str,
        http_client: httpx.AsyncClient,
        rate_limit_client: RateLimitClient,
        resellers_map: Mapping[str, Mapping[str, Any]],
    ):
        self._api_base_url = api_base_url
        self._api_key = api_key
        self._version = version
        self._http_client = http_client
        self._rate_limit_client = rate_limit_client
        self._resellers_map = resellers_map

        self._default_client = client.DuffelClient(
            api_base_url=self._api_base_url,
            api_key=self._api_key,
            version=self._version,
            http_client=self._http_client,
            rate_limit_client=self._rate_limit_client,
        )

    def for_reseller(self, reseller_id: str) -> client.DuffelClient:
        reseller_config = self._resellers_map.get(reseller_id)
        if not reseller_config:
            return self._default_client

        return client.DuffelClient(
            api_base_url=self._api_base_url,
            api_key=reseller_config["api_key"],
            version=self._version,
            http_client=self._http_client,
            rate_limit_client=self._rate_limit_client,
        )
