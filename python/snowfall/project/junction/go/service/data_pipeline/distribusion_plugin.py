"""Distribusion.py.

Download plugin for DISTRIBUSION, a 3rd party aggregator
distribusion works as:
1) Call a URL to get the codes we have access to,
2) Use the code to make the
URL to download the data Returns a tuple of URLs and other stuff.

Note it also does a ClientSession.head call on each code URL to check it is valid.
"""
import os
from collections.abc import Iterator
from pprint import pprint
from typing import Any

from httpx import AsyncClient

from snowfall.project.junction.go.service.data_pipeline.types import Dataset

CARRIER_CODES = ("BLAB", "BRIG", "ESWI", "MEGB", "NEXP")


async def distribusion_plugin(
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    try:
        api_key = os.environ["PIPELINE_DISTRIBUSION_API_KEY"]
    except KeyError as exc:
        raise RuntimeError("Missing DISTRIBUSION_API_KEY env var.") from exc

    headers = {"api-key": api_key}

    # For debugging, log the available carriers.
    resp = await sess.get(
        dataset["url"] + "/retailers/v4/marketing_carriers",  # noqa: WPS336
        headers=headers,
    )
    print("Distribusion: Available codes:")  # noqa: T201,WPS421
    pprint(resp.json()["data"])  # noqa: WPS421,T203

    url = (
        dataset["url"] + "/retailers/v4/marketing_carriers/{code}/gtfs"  # noqa: WPS336
    )
    return ({"url": url.format(code=cd), "headers": headers} for cd in CARRIER_CODES)
