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

    await repo.insert({"_id": "foobar"})
    await repo.insert({"_id": "bazqux"})

    documents = await repo.all_()

    assert isinstance(documents, resultset.ResultSet)
    assert await documents.cursor() == ""

    async for document in documents:
        assert document["_id"] in {"bazqux", "foobar"}

    assert await documents.cursor() != ""
