"""Distribusion.py.

Download plugin for DISTRIBUSION, a 3rd party aggregator
distribusion works as:
1) Call a URL to get the codes we have access to,
2) Use the code to make the
URL to download the data Returns a tuple of URLs and other stuff.

Note it also does a ClientSession.head call on each code URL to check it is valid.
"""
import asyncio
import os
from typing import Any, Iterator, Mapping

from httpx import AsyncClient

from snowfall.project.junction.service.data_pipeline.types import Dataset


async def _check_download_url(
    sess: AsyncClient,
    url: str,
    headers: Mapping[str, str],
) -> str | None:
    """Return True if url is valid, False otherwise.

    VICA currently returns a 404. Can probably remove this after migrating to
    production API.
    """
    resp = await sess.head(url, headers=headers)
    if 200 <= resp.status_code < 300:  # noqa: WPS432
        return url

    print(  # noqa: WPS421
        "distribusion: WARNING cannot download file for: {url}".format(url=url),
    )
    return None


async def _read_distribusion_codes(
    sess: AsyncClient,
    url: str,
    headers: Mapping[str, str],
) -> tuple[str, ...]:
    """Get codes from API (e.g. MEGB, HEXR)."""
    url = "{url}/retailers/v4/marketing_carriers".format(url=url)
    resp = await sess.get(url, headers=headers)
    if not 200 <= resp.status_code < 300:  # noqa: WPS432,WPS508
        raise RuntimeError("Distribusion: Failed to fetch SSIM code data")

    response_data = resp.json()

    return tuple(itm["id"] for itm in response_data["data"])


async def distribusion_plugin(  # noqa: WPS210
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    try:
        api_key = os.environ["PIPELINE_DISTRIBUSION_API_KEY"]
    except KeyError as exc:
        raise RuntimeError("Missing DISTRIBUSION_API_KEY env var.") from exc

    headers = {"api-key": api_key}
    codes = await _read_distribusion_codes(sess, dataset["url"], headers)
    if not codes:
        raise RuntimeError("Distribusion: No codes found.")

    url = (
        dataset["url"] + "/retailers/v4/marketing_carriers/{code}/gtfs"  # noqa: WPS336
    )
    urls = (url.format(code=code) for code in codes)
    tasks = (_check_download_url(sess, url, headers) for url in urls)
    filtered_urls = await asyncio.gather(*tasks)

    return ({"url": url, "headers": headers} for url in filtered_urls if url)
