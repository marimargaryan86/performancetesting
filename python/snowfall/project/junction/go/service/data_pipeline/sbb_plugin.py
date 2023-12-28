"""SBB download plugin.

SBB provides different files for each year, so we need to download both files
for this year and next year (if available).
"""

import asyncio
import datetime
import re
from collections.abc import Iterable, Iterator
from functools import partial
from itertools import chain
from typing import Any

from httpx import AsyncClient

from snowfall.project.junction.go.service.data_pipeline.types import Dataset


async def search_page(
    sess: AsyncClient,
    url: str,
    pattern: re.Pattern[str],
    pg: int,
) -> Iterable[str]:
    resp = await sess.get(url, params={"page": pg})
    if resp.is_success:
        return (mt[0] for mt in pattern.findall(resp.text))
    return ()


async def sbb_plugin(
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    root_url = dataset["url"].removesuffix("/dataset")
    curr_year = datetime.datetime.now(tz=datetime.UTC).year
    pattern = re.compile(
        r'<a href="(.+?)">.*Fahrplan\s*({curr}|{next}).*GTFS.*</a>'.format(
            curr=curr_year,
            next=curr_year + 1,
        ),
    )

    search = partial(search_page, sess, dataset["url"], pattern)
    path_gens = await asyncio.gather(*(search(pg) for pg in range(1, 6)))
    paths = chain.from_iterable(path_gens)

    return ({"url": "{r}{p}/permalink".format(r=root_url, p=pth)} for pth in paths)
