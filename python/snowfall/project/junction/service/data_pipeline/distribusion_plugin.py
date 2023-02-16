"""Distribusion.py.

Download plugin for DISTRIBUSION, a 3rd party aggregator
distribusion works as:
1) Call a URL to get the codes we have access to,
2) Use the code to make the
URL to download the data Returns a tuple of URLs and other stuff.

Note it also does a ClientSession.head call on each code URL to check it is valid.
"""
import os
from typing import Any, Iterator

from httpx import AsyncClient

from snowfall.project.junction.service.data_pipeline.types import Dataset

# Codes for carriers we want to download.
# To view all available carriers, you need the API key, and can then make a request to:
#  | dataset["url"] + "/retailers/v4/marketing_carriers"
# With headers: {"api-key": api_key}
CARRIER_CODES = ("MEGB",)


async def distribusion_plugin(
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    try:
        api_key = os.environ["PIPELINE_DISTRIBUSION_API_KEY"]
    except KeyError as exc:
        raise RuntimeError("Missing DISTRIBUSION_API_KEY env var.") from exc

    headers = {"api-key": api_key}
    url = (
        dataset["url"] + "/retailers/v4/marketing_carriers/{code}/gtfs"  # noqa: WPS336
    )
    return ({"url": url.format(code=cd), "headers": headers} for cd in CARRIER_CODES)
