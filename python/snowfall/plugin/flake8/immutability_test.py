import ast
import textwrap

import pytest

from snowfall.plugin.flake8 import immutability

_FAILING_DATACLASS_NO_CALL = """
import dataclasses

@dataclasses.dataclass
class NoCall:
    pass
"""
_FAILING_DATACLASS_NO_KWARG = """
import dataclasses

@dataclasses.dataclass()
class NoKwarg:
    pass
"""
_FAILING_DATACLASS_NOT_FROZEN = """
import dataclasses

@dataclasses.dataclass(frozen=False)
class NotFrozen:
    pass
"""
_PASSING_DATACLASS_FROZEN = """
import dataclasses

@dataclasses.dataclass(frozen=True)
class Frozen:
    pass
"""


@pytest.mark.parametrize(
    "code,expected",
    [
        (_FAILING_DATACLASS_NO_CALL, 1),
        (_FAILING_DATACLASS_NO_KWARG, 1),
        (_FAILING_DATACLASS_NOT_FROZEN, 1),
        (_PASSING_DATACLASS_FROZEN, 0),
    ],
)
def test_immutability(code: str, expected: int) -> None:
    visitor = immutability.Visitor()
    tree = ast.parse(textwrap.dedent(code))

    visitor.visit(tree)

    assert len(visitor.errors) == expected
