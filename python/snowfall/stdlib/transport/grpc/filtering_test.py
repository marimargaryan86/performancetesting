import pytest

from snowfall.stdlib.format.filter_parser import FilterParser
from snowfall.stdlib.transport.grpc import filtering
from snowfall.stdlib.v1 import testing_pb2


@pytest.mark.parametrize(
    "filter_",
    [
        'id = "foobar"',
        'nested_foobar.id = "foobar"',
    ],
)
def test_parse_with_valid_filter(filter_: str) -> None:
    assert isinstance(
        filtering.parse(testing_pb2.Foobar.DESCRIPTOR, filter_),
        FilterParser.FilterParser.FilterContext,
    )


@pytest.mark.parametrize(
    "filter_",
    [
        "!!!INVALID!!!",
        'foobar = "foobar"',
        'nested_foobar.foobar = "foobar"',
        'foobar.foobar = "foobar"',
        'id.id = "foobar"',
    ],
)
def test_parse_with_invalid_filter(filter_: str) -> None:
    with pytest.raises(filtering.InvalidFilterError):
        filtering.parse(testing_pb2.Foobar.DESCRIPTOR, filter_)
