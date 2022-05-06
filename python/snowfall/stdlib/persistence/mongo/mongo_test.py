import asyncio
from typing import Any

import mongomock_motor
import pytest

from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class MockRepository(
    mixins.AllMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    """Used for tests with various mixins."""


@pytest.mark.asyncio
async def test_result_set() -> None:
    repo = MockRepository(mongomock_motor.AsyncMongoMockClient()["tests"]["test"])

    await asyncio.gather(
        repo.insert({"_id": "foobar_foobar"}),
        repo.insert({"_id": "bazqux_foobar"}),
        repo.insert({"_id": "foobar_bazqux"}),
        repo.insert({"_id": "bazqux_bazqux"}),
    )

    documents = await repo.all_()

    documents.limit(3)

    assert len([document async for document in documents]) == 3

    cursor = await documents.cursor()

    assert cursor != ""

    documents = await repo.all_(cursor=cursor)

    assert isinstance(documents, resultset.ResultSet)

    documents.limit(3)

    assert len([document async for document in documents]) == 1
    assert await documents.cursor() == ""
