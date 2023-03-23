import functools

import httpx

from snowfall.stdlib.transport.http import client


class BenerailBaseClient(client.HttpClient):
    def __init__(
        self,
        subscription_key: str,
        base_url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(base_url, http_client)
        self._subscription_key = subscription_key

    @functools.cached_property
    def _auth_headers(self) -> dict[str, str]:
        return {
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": "{subscription_key}".format(
                subscription_key=self._subscription_key,
            ),
        }

    def _get_headers(self, etag: str | None = None) -> dict[str, str]:
        headers = {
            **self._auth_headers,
            "Content-Type": "application/json",
        }

        if etag:
            headers["If-Match"] = etag

        return headers
