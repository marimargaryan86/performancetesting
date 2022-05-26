import dataclasses
from typing import Optional

from furl import furl
from starlette import requests

PAGE_CURSOR_KEY = "page[cursor]"
PAGE_LIMIT_KEY = "page[limit]"


@dataclasses.dataclass(frozen=True)
class Pagination(object):
    cursor: Optional[str] = None
    limit: Optional[int] = None


def get_pagination(request: requests.Request) -> Pagination:
    limit = request.query_params.get(PAGE_LIMIT_KEY)

    if limit is not None:
        limit = int(limit)

    return Pagination(
        cursor=request.query_params.get(PAGE_CURSOR_KEY),
        limit=limit,
    )


def get_next_url(
    url: str,
    next_page_token: Optional[str],
    pagination: Pagination,
) -> dict[str, Optional[str]]:
    if not next_page_token:
        return {"next": None}

    next_url = furl(url)
    next_url.args[PAGE_CURSOR_KEY] = next_page_token
    next_url.args[PAGE_LIMIT_KEY] = pagination.limit

    return {"next": next_url.url}
