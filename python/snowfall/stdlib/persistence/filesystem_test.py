import pathlib
from collections.abc import AsyncIterator

import pytest

from snowfall.stdlib.persistence import filesystem


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


class TestStorage(object):
    async def test_file_can_be_created(self, storage: filesystem.Storage) -> None:
        path = pathlib.Path("foo")
        body = b"foo"
        await storage.put(path, body)
        fetched_body = await storage.get(path)
        assert fetched_body == body

    async def test_file_raises_error(self, storage: filesystem.Storage) -> None:
        with pytest.raises(filesystem.NotFoundError):
            await storage.get(pathlib.Path("foo"))
