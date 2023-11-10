from urllib import parse as urllib_parse

import pytest
from starlette import datastructures, requests

from snowfall.stdlib.integration.starlette import urls
from snowfall.stdlib.v1 import sort_pb2


@pytest.mark.parametrize(
    ("starlette_request", "expected"),
    [
        (
            requests.Request(scope={"type": "http", "query_string": ""}),
            urls.QueryParams(),
        ),
        (
            requests.Request(
                scope={"type": "http", "query_string": "page[cursor]=foobar"},
            ),
            urls.QueryParams(
                pagination=urls.PaginationQueryParams(
                    cursor="foobar",
                ),
            ),
        ),
        (
            requests.Request(
                scope={
                    "type": "http",
                    "query_string": "page[cursor]=foobar&page[limit]=5",
                },
            ),
            urls.QueryParams(
                pagination=urls.PaginationQueryParams(
                    cursor="foobar",
                    limit=5,
                ),
            ),
        ),
        (
            requests.Request(
                scope={
                    "type": "http",
                    "query_string": "page[cursor]=foobar&foobar=bazqux",
                },
            ),
            urls.QueryParams(
                pagination=urls.PaginationQueryParams(
                    cursor="foobar",
                ),
            ),
        ),
        (
            requests.Request(
                scope={"type": "http", "query_string": "sort=foobar"},
            ),
            urls.QueryParams(
                sort=urls.SortQueryParams(
                    field="foobar",
                ),
            ),
        ),
        (
            requests.Request(
                scope={
                    "type": "http",
                    "query_string": "sort=-foobar",
                },
            ),
            urls.QueryParams(
                sort=urls.SortQueryParams(
                    field="foobar",
                    direction=sort_pb2.Sort.ORDER_DESCENDING,
                ),
            ),
        ),
        (
            requests.Request(
                scope={
                    "type": "http",
                    "query_string": "sort=foobar&foobar=bazqux",
                },
            ),
            urls.QueryParams(
                sort=urls.SortQueryParams(
                    field="foobar",
                ),
            ),
        ),
        (
            requests.Request(
                scope={
                    "type": "http",
                    "query_string": "page[cursor]=foobar&page[limit]=5&sort=-foobar",
                },
            ),
            urls.QueryParams(
                pagination=urls.PaginationQueryParams(
                    cursor="foobar",
                    limit=5,
                ),
                sort=urls.SortQueryParams(
                    field="foobar",
                    direction=sort_pb2.Sort.ORDER_DESCENDING,
                ),
            ),
        ),
    ],
)
def test_query_params_can_be_parsed(
    starlette_request: requests.Request,
    expected: urls.QueryParams,
) -> None:
    assert urls.QueryParams.from_request(starlette_request) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            datastructures.URL("https://example.com"),
            datastructures.URL(
                "https://example.com?{0}".format(
                    urllib_parse.urlencode({"page[cursor]": "foobar"}),
                ),
            ),
        ),
        (
            datastructures.URL(
                "https://example.com?{0}".format(
                    urllib_parse.urlencode({"page[cursor]": "bazqux"}),
                ),
            ),
            datastructures.URL(
                "https://example.com?{0}".format(
                    urllib_parse.urlencode({"page[cursor]": "foobar"}),
                ),
            ),
        ),
        (
            datastructures.URL(
                "https://example.com?{0}".format(
                    urllib_parse.urlencode(
                        {"page[limit]": 5, "page[cursor]": "bazqux"},
                    ),
                ),
            ),
            datastructures.URL(
                "https://example.com?{0}".format(
                    urllib_parse.urlencode(
                        {"page[limit]": 5, "page[cursor]": "foobar"},
                    ),
                ),
            ),
        ),
    ],
)
def test_replace_cursor(url: datastructures.URL, expected: datastructures.URL) -> None:
    assert str(urls.replace_cursor(url, "foobar")) == str(expected)
