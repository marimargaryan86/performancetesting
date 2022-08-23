import ast

import pytest

from snowfall.plugin.flake8 import plugin


@pytest.mark.parametrize(
    "source,expected",
    [
        [
            "_: str",
            "str",
        ],
        [
            "_: list[str]",
            "list",
        ],
        [
            "_: foo.bar",
            "foo.bar",
        ],
        [
            "_: foo.bar.baz",
            "foo.bar.baz",
        ],
        [
            "_: str | int",
            "typing.Union",
        ],
        [
            "_: str | int | bytes",
            "typing.Union",
        ],
        [
            "_: {request}",
            "typing.Set",
        ],
        [
            "_: None",
            "None",
        ],
    ],
)
def test_resolve_fullname(source: str, expected: str) -> None:
    assignment = ast.parse(source).body[0]

    assert isinstance(assignment, ast.AnnAssign)
    assert plugin.resolve_fullname(assignment.annotation) == expected
