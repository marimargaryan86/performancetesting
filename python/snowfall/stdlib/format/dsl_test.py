import pytest

from snowfall.stdlib.format import dsl
from snowfall.stdlib.format.filter_parser import FilterParser


def test_parse_filter_parses_valid_syntax() -> None:
    assert isinstance(
        dsl.parse_filter("a = b"),
        FilterParser.FilterParser.FilterContext,
    )


def test_parse_filter_raises_on_invalid_syntax() -> None:
    with pytest.raises(dsl.ParseError):
        dsl.parse_filter("!!!INVALID!!!")
