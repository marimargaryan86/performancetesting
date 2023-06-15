import base64
import binascii
import dataclasses
from collections.abc import Sequence
from typing import Generic, TypeGuard, TypeVar, cast

from snowfall.stdlib.persistence import cursor as std_cursor

_DEFAULT_PAGE_LIMIT = 20
_NotList = TypeVar("_NotList")
_Resource = TypeVar("_Resource")


@dataclasses.dataclass(frozen=True)
class Page(Generic[_Resource]):
    sequence: Sequence[_Resource]
    cursor: str


def ensure(maybe_list: Sequence[_NotList] | _NotList) -> Sequence[_NotList]:
    if not is_a(maybe_list):
        return [cast(_NotList, maybe_list)]

    return maybe_list


def is_a(maybe_list: Sequence[_NotList] | _NotList) -> TypeGuard[Sequence[_NotList]]:
    return isinstance(maybe_list, Sequence) and not isinstance(maybe_list, str | bytes)


def paginate(
    sequence: Sequence[_Resource],
    cursor: str | None = None,
    limit: int | None = None,
) -> Page[_Resource]:
    start_index = 0

    if cursor:
        start_index = int(std_cursor.unmarshal(cursor, None).id)

    end_index = start_index + (limit or _DEFAULT_PAGE_LIMIT)
    cursor = std_cursor.marshal(std_cursor.new(str(end_index), None, None, None))

    return Page(
        sequence=sequence[start_index:end_index],
        cursor=cursor,
    )


class InvalidCompositeError(ValueError):
    """Raised when an invalid composite ID is unmarshalled."""


def from_composite_id(identifier: str) -> Sequence[str]:
    try:
        raw = base64.urlsafe_b64decode(identifier).decode()
    except binascii.Error as err:
        raise InvalidCompositeError from err

    return raw.rstrip("\x00").split("\x00")


def to_composite_id(parts: Sequence[str]) -> str:
    raw = "\x00".join(parts)

    while len(raw) % 3 != 0:
        raw = "{0}\x00".format(raw)

    return base64.urlsafe_b64encode(raw.encode()).decode()
