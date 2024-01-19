import time
from collections.abc import AsyncGenerator

import httpx

from snowfall.stdlib.transport.http import client as http_client
from snowfall.vendor.fluxir.models import access_token as access_token_models
from snowfall.vendor.fluxir.models import travel_services as travel_services_models


class FluxirAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        tenant_id: str,
    ):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._tenant_id = tenant_id
        self._token: access_token_models.AccessTokenResponse | None = None
        self._token_last_retrieved_at_timestamp: float | None = None
        self._client = httpx.AsyncClient()
        self._client.base_url = httpx.URL(base_url)
        self._client.headers.update({
            "X-Tenant": self._tenant_id,
            "Api-Version": "v1",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
        })

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        if self._is_token_expired():
            self._token = await self._retrieve_token()
            self._token_last_retrieved_at_timestamp = time.time()

        if self._token:
            request.headers.update({
                "Authorization": "Bearer {0}".format(self._token.access_token),
            })

        yield request

    async def _retrieve_token(self) -> access_token_models.AccessTokenResponse:
        response = await self._client.request(
            url="connect/token",
            method="POST",
            data={
                "username": self._username,
                "password": self._password,
            },
        )
        response_body = response.json()

        return access_token_models.AccessTokenResponse(**response_body)

    def _is_token_expired(
        self,
    ) -> bool:
        if self._token_last_retrieved_at_timestamp is None or self._token is None:
            return True

        safety_margin = 300

        return (
            self._token_last_retrieved_at_timestamp
            + self._token.expires_in
            + safety_margin
            > time.time()
        )


class FluxirClient(http_client.HttpClient):
    _token: access_token_models.AccessTokenResponse | None
    _token_created_at_timestamp: float | None = None

    def __init__(
        self,
        base_url: str,
        auth: FluxirAuth,
        tenant_id: str,
        client: httpx.AsyncClient,
    ):
        client.auth = auth
        client.headers.update({
            "X-Tenant": tenant_id,
            "Api-Version": "v1",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
        })
        super().__init__(base_url, client)

    async def get_service_intents(
        self,
        request: travel_services_models.GetServiceIntentsRequest,
    ) -> travel_services_models.GetServiceIntentsResponse:
        params = request.model_dump()

        response = await self._make_request(
            http_client.RequestOptions(
                path="travel-services/service-intents",
                method="GET",
                query={
                    "from": params.get("from_", ""),
                    "to": params.get("to", ""),
                    "nationalityCountryCode": params.get(
                        "nationality_country_code",
                        "",
                    ),
                    "destinationCountryCode": params.get(
                        "destination_country_code",
                        "",
                    ),
                    "tripPurpose": params.get("trip_purpose", ""),
                },
            ),
        )
        response_body = response.json()

        return travel_services_models.GetServiceIntentsResponse(**response_body)
