from typing import Any, Mapping

import httpx


class PlusClient(object):
    def __init__(
        self,
        api_url: str,
        activated: bool,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)
        self._activated = activated
        self._client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

    async def register_order(self, mobile_order_id: str) -> None:
        body = {
            "data": {
                "attributes": {},
                "relationships": {
                    "orders": {"data": {"id": mobile_order_id, "type": "orders"}},
                },
                "type": "whatsapp-registrations",
            },
        }
        await self._make_request(
            method="POST",
            url="/register",
            payload=body,
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> None:
        if self._activated:
            response = await self._client.request(
                method=method,
                url=url,
                params=query_parameters,
                json=payload,
            )

            response.raise_for_status()
