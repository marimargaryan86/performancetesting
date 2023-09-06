import dataclasses
import datetime

import httpx


@dataclasses.dataclass(frozen=True)
class AuthServiceResponse(object):
    token: str
    expires_at: datetime.datetime


class AuthClient(object):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_url: str,
        client_id: str,
        client_secret: str,
    ):
        self._http_client = http_client
        self._api_url = api_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret

        self._auth_response: AuthServiceResponse | None = None

    async def get_token(self) -> str:
        if not self._is_token_valid():
            self._auth_response = await self._create_token()

        return self._auth_response.token  # type: ignore[union-attr]

    def _is_token_valid(self) -> bool:
        return bool(
            self._auth_response
            and self._auth_response.expires_at > datetime.datetime.now(tz=datetime.UTC),
        )

    async def _create_token(self) -> AuthServiceResponse:
        request_data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        }

        start = datetime.datetime.now(tz=datetime.UTC)

        response = await self._http_client.post(
            url="{0}/oauth2/token".format(self._api_url),
            data=request_data,
        )
        response.raise_for_status()
        response_data = response.json()

        expires_at = start + datetime.timedelta(seconds=response_data["expires_in"])

        return AuthServiceResponse(
            token=response_data["access_token"],
            expires_at=expires_at,
        )
