import pathlib

import aiofiles
import httpx


async def fetch_feed(filename: pathlib.Path, feed_url: str, user_agent: str) -> None:
    async with httpx.AsyncClient(headers={"User-Agent": user_agent}) as client:
        async with client.stream(
            "GET",
            feed_url,
            follow_redirects=True,
        ) as response:
            response.raise_for_status()

            async with aiofiles.open(str(filename), mode="wb") as feed_file:
                async for chunk in response.aiter_bytes():
                    await feed_file.write(chunk)
