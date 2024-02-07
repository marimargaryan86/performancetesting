from collections.abc import Iterator, Mapping, Sequence
from typing import Any

import httpx
from furl import furl

from snowfall.stdlib.persistence import cursor
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

    async def list_identities(
        self,
        page_size: int = 0,
        page_token: str = "",
        ids: Sequence[str] | None = None,
    ) -> models.IdentitiesPage:
        response = await self._client.get(
            url="/admin/identities",
            params=list(
                self._build_list_identities_query_params(
                    ids=ids,
                    page_size=page_size,
                    page_token=page_token,
                ),
            ),
        )
        response.raise_for_status()

        next_page_token = None
        next_link = response.links.get("next", {})
        if next_link:
            url = furl(next_link.get("url"))
            next_page_token = cursor.new(
                url.args.get("page_token", ""),
                ids,
                None,
                None,
            )

        return models.IdentitiesPage(
            identities=[models.Identity(**identity) for identity in response.json()],
            next_page_token=next_page_token,
        )

    async def get_identity(self, identifier: str) -> models.Identity:
        response = await self._client.get(
            url="/admin/identities/{0}".format(identifier),
        )
        response.raise_for_status()

        return models.Identity(**response.json())

    async def update_identity(
        self,
        identity: models.Identity,
    ) -> models.Identity:
        operations = [
            {
                "op": "replace",
                "path": "/metadata_public/{0}".format(meta_key),
                "value": meta_value,
            }
            for meta_key, meta_value in identity.metadata_public.items()
        ]
        if identity.traits.email:
            operations.append(
                {
                    "op": "replace",
                    "path": "/traits/email",
                    "value": identity.traits.email,
                },
            )
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
            url="/admin/identities",
            json={
                "metadata_public": metadata,
                "schema_id": self._schema_id,
                "state": "active",
                "traits": {"email": email},
            },
        )
        response.raise_for_status()

        return models.Identity(**response.json())

    async def delete_identity(self, identifier: str) -> None:
        response = await self._client.delete(
            url="/admin/identities/{0}".format(identifier),
        )
        response.raise_for_status()

    def _calculate_cookie_name(self) -> str:
        if not self._slug:
            return "ory_kratos_session"

        return "ory_session_{0}".format(self._slug.replace("-", ""))

    def _build_list_identities_query_params(
        self,
        page_size: int = 0,
        page_token: str = "",
        ids: Sequence[str] | None = None,
    ) -> Iterator[tuple[str, str | int]]:
        if page_size:
            yield ("page_size", page_size)
        if page_token:
            yield ("page_token", page_token)
        if ids:
            for identity_id in ids:
                yield ("ids", identity_id)
