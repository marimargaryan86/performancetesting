import asyncio
from collections.abc import AsyncIterable
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
    generator: AsyncIterable[_DataType],
    expected: list[_DataType],
) -> None:
    assert expected == [gen_item async for gen_item in generator]  # nosec
