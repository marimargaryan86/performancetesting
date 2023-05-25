from unittest import mock

import pytest
from starlette import requests

from snowfall.stdlib.integration.starlette import sorting
from snowfall.stdlib.v1 import sort_pb2


def _get_mock_request(sort: str) -> requests.Request:
    request = mock.create_autospec(requests.Request)
    request.scope = {"parsed_query_string": {"sort": sort}}

    return request


@pytest.mark.parametrize(
    ("sort_parameter", "expected"),
    [
        (
            _get_mock_request("fooBar"),
            sort_pb2.Sort(field="foo_bar", order=sort_pb2.Sort.ORDER_ASCENDING),
        ),
        (
            _get_mock_request("-fooBar"),
            sort_pb2.Sort(field="foo_bar", order=sort_pb2.Sort.ORDER_DESCENDING),
        ),
    ],
)
def test_get_sort(
    sort_parameter: requests.Request,
    expected: str,
) -> None:
    mapping = {"fooBar": "foo_bar"}
    assert sorting.get_sort(sort_parameter, mapping) == expected
