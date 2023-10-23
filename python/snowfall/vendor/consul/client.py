import httpx

from snowfall.stdlib.transport.http import client as http_client
from snowfall.stdlib.transport.http.client import HttpClient


class ConsulClient(HttpClient):
    def __init__(
        self,
        api_base_url: str,
        api_token: str,
        version: str,
        httpx_client: httpx.AsyncClient,
    ) -> None:
        base_url = "{0}/{1}".format(api_base_url.rstrip("/"), version)
        super().__init__(base_url, httpx_client)

        self._token = api_token

    async def get_key(self, key: str) -> bytes:
        response = await self._make_request(
            http_client.RequestOptions(
                method="GET",
                path="kv/{key}".format(key=key.strip("/")),
                headers=self._auth_headers,
                query={
                    "raw": "true",
                },
            ),
        )

        return response.content

    async def put_key(self, key: str, value: bytes) -> bool:
        response = await self._make_request(
            http_client.RequestOptions(
                method="PUT",
                path="kv/{key}".format(key=key.strip("/")),
                headers=self._auth_headers,
                raw_content=value,
            ),
        )

        return response.json()

    @property
    def _auth_headers(self) -> dict[str, str]:
        return {
            "X-Consul-Token": self._token,
        }
