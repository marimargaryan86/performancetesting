import datetime
from typing import Any, Callable, Optional, Sequence, Union

from dateutil.parser import parse as date_parser
from pydantic import typing, validator


def normalize_time(
    time: Optional[Union[float, str]],
) -> Optional[Union[float, datetime.timedelta]]:
    if time is None:
        return None

    if isinstance(time, str):
        # duration: str, e.g. 2h22m
        hours, minutes = date_parser(time).hour, date_parser(time).minute
        return datetime.timedelta(hours=hours, minutes=minutes)

    # A JSON-serialized model will contain float.
    if isinstance(time, float):
        return datetime.timedelta(seconds=time)


def normalize_nullable_fields(field_value: Any) -> Optional[str]:
    if isinstance(field_value, str) and field_value.upper() == "NULL":
        field_value = None
    return field_value


def normalizer(
    properties: Sequence[str],
    func: Callable[[Optional[str]], Any],
) -> "typing.AnyClassMethod":
    return validator(*properties, pre=True, allow_reuse=True)(func)
