import httpx


class BaseClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self._client = client or httpx.AsyncClient(http2=True)
        self._client.base_url = self._base_url
        self._client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

        if auth:
            self._client.auth = auth
