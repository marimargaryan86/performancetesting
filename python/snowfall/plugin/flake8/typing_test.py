import ast
import textwrap

import pytest

from snowfall.plugin.flake8 import typing

_FAILING_LIST = """
def list_(input: list) -> None:
    pass
"""
_FAILING_LIST_TYPE = """
from typing import List

def typing_list(input: List) -> None:
    pass
"""
_PASSING_LIST_TYPE = """
def typing_list(input: List) -> None:
    pass
"""
_FAILING_NESTED_LIST = """
def nested_list(input: list[list[list[list]]]) -> None:
    pass
"""
_FAILING_LIST_IN_CALLABLE = """
from typing import Callable

def list_in_callable(input: Callable[[list], None]) -> list:
    return []
"""
_PASSING_LIST_RETURN = """
def list_return() -> list:
    return []
"""
_PASSING_AWAITABLE_NONE = """
from typing import Awaitable

def none_awaitable(input: Awaitable[None]) -> None:
    return None
"""
_PASSING_CORRECT_MAPPING = """
from typing import Any, Mapping

def correct_function(input: Mapping[str, Any]) -> None:
    return None
"""
_PASSING_CORRECT_SEQUENCE = """
from typing import Any, Sequence

def correct_function(input: Sequence[str]) -> None:
    return None
"""
_FAILING_LIST_IN_BINOP = """
from typing import Callable

def list_in_bin_op(input: list[str] | str) -> list:
    return []
"""
_FAILING_LIST_IN_BINOP_IN_SEQUENCE = """
from typing import Callable

def list_in_bin_op_in_sequence(input: Sequence[list[str] | str]) -> list:
    return []
"""
_FAILING_UNION = """
from typing import Optional, Union

def union(input: Union[str, float]) -> Union[str, float]:
    return input
"""
_FAILING_OPTIONAL = """
from typing import Optional, Union

def union(input: Optional[str]) -> Optional[str]:
    return input
"""


@pytest.mark.parametrize(
    "code,expected",
    [
        (_FAILING_LIST, 1),
        (_FAILING_LIST_TYPE, 1),
        (_PASSING_LIST_TYPE, 0),
        (_FAILING_NESTED_LIST, 4),
        (_FAILING_LIST_IN_CALLABLE, 1),
        (_PASSING_LIST_RETURN, 0),
        (_PASSING_AWAITABLE_NONE, 0),
        (_PASSING_CORRECT_MAPPING, 0),
        (_PASSING_CORRECT_SEQUENCE, 0),
        (_FAILING_LIST_IN_BINOP, 1),
        (_FAILING_LIST_IN_BINOP_IN_SEQUENCE, 1),
        (_FAILING_UNION, 2),
        (_FAILING_OPTIONAL, 2),
    ],
)
def test_typing(code: str, expected: int) -> None:
    visitor = typing.Visitor()
    tree = ast.parse(textwrap.dedent(code))

    visitor.visit(tree)

    assert len(visitor.errors) == expected
