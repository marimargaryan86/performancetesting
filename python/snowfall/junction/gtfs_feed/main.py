import asyncio
import io
from zipfile import ZipFile

import httpx
from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    feed_url: AnyUrl


async def fetch() -> None:
    settings = Settings()

    async with httpx.AsyncClient() as client:
        response = await client.get(settings.feed_url)

        response.raise_for_status()

        with io.BytesIO(response.content) as feed:
            ZipFile(feed)


if __name__ == "__main__":
    asyncio.run(fetch())
