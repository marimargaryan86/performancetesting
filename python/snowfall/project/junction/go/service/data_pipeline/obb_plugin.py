"""OBB download plugin.

OBB has an awkward (seemingly undocumented) API to retrieve their datasets.
"""

import re
from collections.abc import Iterator
from datetime import date
from typing import Any

from httpx import AsyncClient

from snowfall.project.junction.go.service.data_pipeline.types import Dataset


async def _get_auth(sess: AsyncClient) -> str:
    resp = await sess.get("https://data.oebb.at/oebb/DatasetsConfig.js")
    if not 200 <= resp.status_code < 300:  # noqa: WPS432,WPS508
        raise RuntimeError("OBB: Config request failed.")

    config = resp.text
    match = re.search(r"DatasetsConfig.up\s*=\s*'(.*)'", config)
    if not match:
        raise RuntimeError("OBB: Missing auth token.")
    return match.group(1)


def is_old_name(name: str) -> bool:
    """Filter out old versions."""
    match = re.search(r"_\d{4}|\d{4}_", name)
    if match is None:
        return False
    year = int(match.group(0).strip("_"))
    return year < date.today().year


async def obb_plugin(  # noqa: WPS210
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    headers = {"Authorization": "Basic {t}".format(t=await _get_auth(sess))}

    request_params = {"searchValue": "Soll Fahrplan GTFS"}
    resp = await sess.get(dataset["url"], params=request_params, headers=headers)
    if not 200 <= resp.status_code < 300:  # noqa: WPS432,WPS508
        raise RuntimeError("OBB: Failed to fetch opendata.")

    docs = resp.json()
    if len(docs["openDataDocuments"]) > 1:
        raise RuntimeError("OBB: Too many results")

    resources = docs["openDataDocuments"][0]["datenUndResourcen"]
    # This may match multiple resources (e.g. 2022 and 2023).
    links = (
        rs["link"]
        for rs in resources
        if "GFTS_Fahrplan_OEBB" in rs["name"] and not is_old_name(rs["name"])
    )

    url = "{r}/download".format(r=dataset["url"])
    return ({"url": url, "params": {"url": lnk}, "headers": headers} for lnk in links)
