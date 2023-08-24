import datetime
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from dateutil.parser import parse as date_parser
from pydantic.v1 import typing, validator


def normalize_time(
    time: float | str | None,
) -> datetime.timedelta | None:
    if isinstance(time, str):
        # duration: str, e.g. 2h22m
        hours, minutes = date_parser(time).hour, date_parser(time).minute
        return datetime.timedelta(hours=hours, minutes=minutes)

    # A JSON-serialized model will contain float.
    if isinstance(time, int | float):
        return datetime.timedelta(seconds=time)

    return None


_Input = TypeVar("_Input")


def normalize_nullable_fields(field_value: _Input | None) -> _Input | None:
    if isinstance(field_value, str) and field_value.upper() == "NULL":
        return None

    return field_value


def normalizer(
    properties: Sequence[str],
    func: Callable[[str | None], Any],
) -> "typing.AnyClassMethod":
    return validator(*properties, pre=True, allow_reuse=True)(func)
