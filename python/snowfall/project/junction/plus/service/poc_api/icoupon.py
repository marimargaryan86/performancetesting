import datetime
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from snowfall.stdlib import string


class ICouponClient(object):
    def __init__(
        self,
        api_url: str,
        client_id: str,
        client_secret: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)
        self._token = None
        self._token_expires = datetime.datetime.now(tz=datetime.UTC)

    async def create_campaign(self, quantity: int) -> Sequence[Mapping[str, Any]]:
        now = datetime.datetime.now(tz=datetime.UTC)

        response = await self._client.request(
            method="POST",
            url="/v1/campaigns/campaignCodes",
            json={
                "customerCode": "SNO",
                "voucherTypeRef": "GR20EUR",
                "reference": string.uuid(),
                "validFrom": (now + datetime.timedelta(minutes=5)).isoformat(),
                "validTo": (now + datetime.timedelta(hours=5)).isoformat(),
                "quantity": quantity,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(await self._get_token()),
            },
        )

        response.raise_for_status()

        return response.json()["barcodes"]

    async def _get_token(self) -> str:
        if datetime.datetime.now(tz=datetime.UTC) < self._token_expires:
            return self._token  # type: ignore[return-value]
        response = await self._client.request(
            method="POST",
            url="/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self._token = response.json()["access_token"]
        self._token_expires = datetime.datetime.strptime(
            response.json()[".expires"],
            "%a, %d %b %Y %H:%M:%S %Z",
        ).replace(tzinfo=datetime.UTC)
        return self._token  # type: ignore[return-value]
