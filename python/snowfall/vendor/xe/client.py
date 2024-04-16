import base64
from collections.abc import AsyncGenerator, Sequence

import httpx

from snowfall.stdlib.logging import stdout
from snowfall.vendor.xe.models import rate


class XEAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        login_id: str,
        api_key: str,
    ):
        self._logger = stdout.get_logger()
        self._token = base64.b64encode(
            "{0}:{1}".format(login_id, api_key).encode(),
        ).decode()

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers["Authorization"] = "Basic {0}".format(
            self._token,
        )
        response = yield request

        if response.status_code == httpx.codes.UNAUTHORIZED:
            self._logger.info("Authorization is failed")


class XEClient:
    def __init__(
        self,
        base_url: str,
        auth: XEAuth,
    ):
        self._client = httpx.AsyncClient(
            auth=auth,
            base_url=base_url,
        )

    async def convert(
        self,
        from_currency: str,
        to_currencies: Sequence[str],
        amount: int = 1,
    ) -> Sequence[rate.RateResponse]:
        response = await self._client.get(
            "/convert_from",
            params={
                "from": from_currency,
                "to": ",".join(to_currencies),
                "amount": amount,
            },
        )

        response.raise_for_status()
        response_data = response.json()

        return [
            rate.RateResponse(
                from_currency=from_currency,
                to_currency=response["quotecurrency"],
                rate=response["mid"],
            )
            for response in response_data["to"]
        ]
