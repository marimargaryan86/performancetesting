import httpx

from snowfall.vendor.ory import models


class OryClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self._client = client or httpx.AsyncClient()
        self._client.base_url = self._base_url

        if auth:
            self._client.auth = auth

    async def get_client_by_id(self, identifier: str) -> models.OAuth2Client:
        response = await self._client.get(url="/admin/clients/{0}".format(identifier))
        response.raise_for_status()

        return models.OAuth2Client(**response.json())
