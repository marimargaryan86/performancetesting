import asyncio
import collections
from collections.abc import AsyncIterable, Iterable
from typing import Awaitable, TypeVar

_DataType = TypeVar("_DataType")


async def assert_awaitables(
    *aws_and_expected: tuple[Awaitable[_DataType], _DataType],
) -> None:
    returned_values = await asyncio.gather(
        *[aws for aws, expected in aws_and_expected],
    )

    for index, expected in enumerate([expected for aws, expected in aws_and_expected]):
        assert returned_values[index] == expected  # nosec


async def assert_iterable(
    generator: AsyncIterable[_DataType] | Iterable[_DataType],
    expected: Iterable[_DataType],
) -> None:
    if isinstance(generator, AsyncIterable):
        assert collections.Counter(expected) == collections.Counter(  # nosec
            [gen_item async for gen_item in generator],
        )
    else:
        assert collections.Counter(expected) == collections.Counter(  # nosec
            list(generator),
        )
