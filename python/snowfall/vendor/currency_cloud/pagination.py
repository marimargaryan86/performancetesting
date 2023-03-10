from typing import Dict, Mapping, Optional

import currencycloud
from furl import furl


class Pagination(object):
    def __init__(
        self,
        cursor: Optional[str],
        limit: Optional[int],
        sort: Optional[str],
        url: str,
    ):
        self._cursor: Optional[str] = cursor
        self._limit: Optional[int] = limit
        self._sort: Optional[str] = sort
        self._pagination_params = {
            "order": self._sort,
            "page": self._cursor,
            "per_page": self._limit,
        }
        self._url = url
        self._next_url: dict[str, str] = {}

    @property
    def pagination_params(self) -> Dict[str, str | int]:
        return {
            pag_k: pag_v for pag_k, pag_v in self._pagination_params.items() if pag_v
        }

    @property
    def next_url(
        self,
    ) -> Mapping[str, str]:
        return self._next_url

    @next_url.setter
    def next_url(
        self,
        pagination: currencycloud.resources.pagination.Pagination,
    ) -> None:
        next_url = furl(self._url)
        next_url.args["page[cursor]"] = pagination.next_page
        next_url.args["page[limit]"] = pagination.per_page

        self._next_url["next"] = next_url.url
