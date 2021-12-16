import asyncio
import os

import aiofiles
import httpx
from pydantic import AnyUrl, BaseSettings


class _Settings(BaseSettings):
    feed_url: AnyUrl


async def _main() -> None:
    settings = _Settings()

    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        filename = os.path.join(tempdir, "feed.zip")

        await _fetch(filename, settings)


async def _fetch(filename: str, settings: _Settings) -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            settings.feed_url,
            follow_redirects=True,
        ) as response:

            response.raise_for_status()

            async with aiofiles.open(filename, mode="wb") as feed_file:
                async for chunk in response.aiter_bytes():
                    await feed_file.write(chunk)


if __name__ == "__main__":
    asyncio.run(_main())
