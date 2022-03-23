from typing import Any

import pytest

from snowfall.stdlib import dictionary


def _transform(dict_value: str) -> str:
    return dict_value.upper()


@pytest.mark.parametrize(
    "input_dict,path,expected",
    [
        ({"foo": "bar"}, "foo", {"foo": "BAR"}),
        ({"foo": {"bar": "baz"}}, "foo.bar", {"foo": {"bar": "BAZ"}}),
        ({"foo": None}, "foo.bar", {"foo": None}),
        (
            {"foo": [{"bar": "baz"}, {"bar": "baz"}]},
            "foo.bar",
            {"foo": [{"bar": "BAZ"}, {"bar": "BAZ"}]},
        ),
    ],
)
async def test_set_nested_value(
    input_dict: dict[str, Any],
    path: str,
    expected: dict[str, Any],
) -> None:
    dictionary.set_nested_value(
        input_dict,
        path.split("."),
        _transform,
    )

    assert input_dict == expected
