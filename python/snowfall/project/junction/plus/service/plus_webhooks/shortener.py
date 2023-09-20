import abc

import httpx


class Client(abc.ABC):
    @abc.abstractmethod
    async def shorten_link(
        self,
        original_link: str,
    ) -> str:
        """Shorten link via 3rd part api."""


class DictClient(Client):
    async def shorten_link(
        self,
        original_link: str,
    ) -> str:
        return "https://shorten.url"


class ShortenerClient(Client):
    def __init__(
        self,
        shortener_url: str,
        shortener_key: str,
        shortener_domain: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._shortener_url = shortener_url
        self._shortener_key = shortener_key
        self._shortener_domain = shortener_domain
        self._client = client or httpx.AsyncClient()

    async def shorten_link(
        self,
        original_link: str,
    ) -> str:
        response = await self._client.post(
            self._shortener_url,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": self._shortener_key,
            },
            json={
                "domain": self._shortener_domain,
                "originalURL": original_link,
            },
        )
        response.raise_for_status()

        return response.json()["shortURL"]
