import dataclasses
from collections.abc import Sequence
from typing import Any, Optional

from snowfall.stdlib.persistence import cursor as std_cursor

_DEFAULT_PAGE_LIMIT = 20


@dataclasses.dataclass(frozen=True)
class Page(object):
    sequence: Sequence[Any]
    cursor: str


def paginate(
    sequence: Sequence[Any],
    cursor: Optional[str] = None,
    limit: Optional[int] = None,
) -> Page:
    start_index = 0

    if cursor:
        start_index = int(std_cursor.unmarshal(cursor, None).id)

    end_index = start_index + (limit or _DEFAULT_PAGE_LIMIT)
    cursor = std_cursor.marshal(std_cursor.new(str(end_index), None))

    return Page(
        sequence=sequence[start_index:end_index],
        cursor=cursor,
    )
