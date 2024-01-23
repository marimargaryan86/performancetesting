from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.vendor.ory import models


class OryClient(object):
    def __init__(
        self,
        base_url: str,
        slug: str | None = None,
        auth: httpx.Auth | None = None,
        schema_id: str | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self._slug = slug
        self._client = client or httpx.AsyncClient()
        self._client.base_url = self._base_url
        self._cookie_name = self._calculate_cookie_name()

        if auth:
            self._client.auth = auth

        self._schema_id = schema_id

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

    async def list_identities(self) -> list[models.Identity]:
        response = await self._client.get(url="/admin/identities")
        response.raise_for_status()

        return [models.Identity(**identity) for identity in response.json()]

    async def get_identity(self, identifier: str) -> models.Identity:
        response = await self._client.get(
            url="/admin/identities/{0}".format(identifier),
        )
        response.raise_for_status()

        return models.Identity(**response.json())

    async def update_identity(self, identity: models.Identity) -> models.Identity:
        operations = [
            {
                "op": "replace",
                "path": "/metadata_public/{0}".format(meta_key),
                "value": meta_value,
            }
            for meta_key, meta_value in identity.metadata_public.items()
        ]
        response = await self._client.patch(
            url="/admin/identities/{0}".format(identity.identifier),
            json=operations,
        )
        response.raise_for_status()

        return models.Identity(**response.json())

    async def create_identity(
        self,
        email: str,
        metadata: Mapping[str, Any],
    ) -> models.Identity:
        response = await self._client.post(
            url="/admin/identities/",
            json={
                "metadata_public": metadata,
                "schema_id": self._schema_id,
                "state": "active",
                "traits": {"email": email},
            },
        )
        response.raise_for_status()

        return models.Identity(**response.json())

    def _calculate_cookie_name(self) -> str:
        if not self._slug:
            return "ory_kratos_session"

        return "ory_session_{0}".format(self._slug.replace("-", ""))
