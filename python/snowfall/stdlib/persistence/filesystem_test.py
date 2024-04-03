import pathlib
from collections.abc import AsyncIterator

import pytest

from snowfall.stdlib.persistence import filesystem


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


class TestStorage:
    async def test_file_can_be_created(self, storage: filesystem.Storage) -> None:
        path = pathlib.Path("foo")
        body = b"foo"
        await storage.put(path, body)
        fetched_body = await storage.get(path)
        assert fetched_body == body

    async def test_file_raises_error(self, storage: filesystem.Storage) -> None:
        with pytest.raises(filesystem.NotFoundError):
            await storage.get(pathlib.Path("foo"))

    async def test_url_can_be_created(self, storage: filesystem.Storage) -> None:
        path = pathlib.Path("folder1/filename1.pdf")
        expected_url = "http://mock.junction.dev/{0}/folder1/filename1.pdf".format(
            storage._base_path,  # noqa: SLF001
        )
        url = await storage.url(path, 120)
        assert url == expected_url
