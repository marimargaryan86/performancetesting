from __future__ import annotations

import dataclasses
from typing import Self

from starlette import datastructures, requests

from snowfall.stdlib.v1 import sort_pb2

_PAGINATION_CURSOR_KEY = "page[cursor]"
_PAGINATION_LIMIT_DEFAULT = 20
_PAGINATION_LIMIT_KEY = "page[limit]"
_SORT_KEY = "sort"


@dataclasses.dataclass(frozen=True)
class PaginationQueryParams:
    cursor: str | None = None
    limit: int = _PAGINATION_LIMIT_DEFAULT


@dataclasses.dataclass(frozen=True)
class SortQueryParams:
    direction: sort_pb2.Sort.Order.ValueType = sort_pb2.Sort.ORDER_ASCENDING
    field: str | None = None


@dataclasses.dataclass(frozen=True)
class QueryParams:
    pagination: PaginationQueryParams = dataclasses.field(
        default_factory=PaginationQueryParams,
    )
    sort: SortQueryParams = dataclasses.field(default_factory=SortQueryParams)

    @classmethod
    def from_request(cls, request: requests.Request) -> Self:
        params = request.scope.get("parsed_query_string", request.query_params)
        sort_parameter = params.get(_SORT_KEY)
        sort_field = sort_parameter.removeprefix("-") if sort_parameter else None

        return cls(
            pagination=PaginationQueryParams(
                cursor=params.get(_PAGINATION_CURSOR_KEY),
                limit=int(params.get(_PAGINATION_LIMIT_KEY, _PAGINATION_LIMIT_DEFAULT)),
            ),
            sort=SortQueryParams(
                field=sort_field,
                direction=(
                    sort_pb2.Sort.ORDER_ASCENDING
                    if sort_parameter == sort_field
                    else sort_pb2.Sort.ORDER_DESCENDING
                ),
            ),
        )


def replace_cursor(url: datastructures.URL, cursor: str) -> datastructures.URL:
    return url.include_query_params(**{_PAGINATION_CURSOR_KEY: cursor})
