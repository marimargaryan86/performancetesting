import httpx
import more_itertools

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
        self._cookie_name = self._calculate_cookie_name()

        if auth:
            self._client.auth = auth

    @property
    def jwk_url(self) -> str:
        return str(self._base_url.join("/.well-known/jwks.json"))

    async def get_client_by_id(self, identifier: str) -> models.OAuth2Client:
        response = await self._client.get(url="/admin/clients/{0}".format(identifier))
        response.raise_for_status()

        return models.OAuth2Client(**response.json())

    async def get_session(self, cookie: str) -> models.Session:
        response = await self._client.get(
            url="/sessions/whoami",
            cookies={self._cookie_name: cookie},
        )
        response.raise_for_status()

        return models.Session(**response.json())

    def _calculate_cookie_name(self) -> str:
        if not self._base_url.host.endswith("projects.oryapis.com"):
            return "ory_kratos_session"

        ory_project_slug = more_itertools.first(self._base_url.host.split("."))

        return "ory_session_{0}".format(ory_project_slug.replace("-", ""))
