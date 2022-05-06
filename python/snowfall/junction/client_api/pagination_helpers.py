import dataclasses
from typing import Any, Optional, Sequence

from furl import furl
from starlette import requests

from snowfall.stdlib.persistence import cursor

_DEFAULT_PAGE_LIMIT = 20
PAGE_CURSOR_KEY = "page[cursor]"
PAGE_LIMIT_KEY = "page[limit]"


@dataclasses.dataclass(frozen=True)
class Pagination(object):
    cursor: Optional[str] = None
    limit: Optional[int] = None


@dataclasses.dataclass(frozen=True)
class SequencePage(object):
    sequence: Sequence[Any]
    next_page_token: str


def sequence_paginator(
    sequence: Sequence[Any],
    pagination: Pagination,
) -> SequencePage:
    start_index = 0

    if pagination.cursor:
        start_index = int(cursor.unmarshal(pagination.cursor, None).id)

    end_index = start_index + (pagination.limit or _DEFAULT_PAGE_LIMIT)

    if len(sequence) <= end_index:
        next_page_token = ""  # nosec
    else:
        next_page_token = cursor.marshal(cursor.new(str(end_index), None))

    return SequencePage(
        sequence=sequence[start_index:end_index],
        next_page_token=next_page_token,
    )


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
