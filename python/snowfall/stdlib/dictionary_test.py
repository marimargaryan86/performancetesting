from collections.abc import Mapping

import pytest

from snowfall.stdlib import dictionary


def _transform(dict_value: object) -> object:
    return dict_value.upper() if isinstance(dict_value, str) else dict_value


@pytest.mark.parametrize(
    ("input_dict", "path", "expected"),
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
def test_set_nested_value(
    input_dict: Mapping[str, object],
    path: str,
    expected: Mapping[str, object],
) -> None:
    new_dict = dictionary.set_nested_value(
        input_dict,
        path.split("."),
        _transform,
    )

    assert new_dict == expected
