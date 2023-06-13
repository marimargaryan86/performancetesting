"""SBB download plugin.

SBB provides different files for each year, so we need to download both files
for this year and next year (if available).
"""

import datetime
import re
from collections.abc import Iterator
from typing import Any

from httpx import AsyncClient

from snowfall.project.junction.go.service.data_pipeline.types import Dataset


async def sbb_plugin(  # noqa: WPS210
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    root_url = dataset["url"].removesuffix("/dataset")
    curr_year = datetime.date.today().year
    pattern = r'<a href="(.+?)">.*Fahrplan\s*({curr}|{next}).*GTFS.*</a>'.format(
        curr=curr_year,
        next=curr_year + 1,
    )

    resp = await sess.get(dataset["url"])
    if not 200 <= resp.status_code < 300:  # noqa: WPS432,WPS508
        raise RuntimeError("SBB: Lookup failed")

    page = resp.text
    paths = (mt[0] for mt in re.findall(pattern, page))

    return ({"url": "{r}{p}/permalink".format(r=root_url, p=pth)} for pth in paths)
