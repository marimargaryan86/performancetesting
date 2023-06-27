"""OBB download plugin.

OBB has an awkward (seemingly undocumented) API to retrieve their datasets. This
has been reverse-engineered from their main website: https://data.oebb.at
"""

import datetime
import re
from collections.abc import Iterator, Sequence
from contextlib import suppress
from html.parser import HTMLParser
from typing import Any

from httpx import AsyncClient

from snowfall.project.junction.go.service.data_pipeline.types import Dataset


class OBBParser(HTMLParser):
    """Extract download links from HTML."""

    def __init__(self) -> None:
        self.inside_li = False
        self.inside_title = False
        self.save_current = False
        self.downloads: list[str] = []
        super().__init__()

    def handle_starttag(  # noqa: WPS231
        self,
        tag: str,
        attrs: Sequence[tuple[str, str | None]],
    ) -> None:
        if tag == "li":
            with suppress(StopIteration):
                if "od-resources__item" in self._get_attr(attrs, "class"):
                    self.inside_li = True
        elif tag == "h4" and self.inside_li:
            self.inside_title = True
        elif tag == "a" and self.save_current:
            self.downloads.append(self._get_attr(attrs, "href"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "li":
            self.inside_li = False
            self.save_current = False
        elif tag == "h4":
            self.inside_title = False

    def handle_data(self, data: str) -> None:  # noqa: WPS110
        if self.inside_title and "GTFS Fahrplan ÖBB" in data and not is_old_name(data):
            self.save_current = True

    def _get_attr(self, attrs: Sequence[tuple[str, str | None]], name: str) -> str:
        return next(
            txt for tag, txt in attrs if tag == name and txt is not None
        )  # noqa: WPS221


def is_old_name(name: str) -> bool:
    """Filter out old versions."""
    match = re.search(r"( |^)\d{4}( |$)", name)
    if match is None:
        return False
    year = int(match.group(0).strip("_"))
    return year < datetime.datetime.now(tz=datetime.UTC).year


async def obb_plugin(  # noqa: WPS210
    sess: AsyncClient,
    dataset: Dataset,
) -> Iterator[dict[str, Any]]:
    resp = await sess.get(dataset["url"])
    if not 200 <= resp.status_code < 300:  # noqa: WPS432,WPS508
        raise RuntimeError("OBB: Failed to fetch opendata.")

    parser = OBBParser()
    parser.feed(resp.text)
    if not parser.downloads:
        raise RuntimeError("OBB: No downloads found")

    return ({"url": url} for url in parser.downloads)
