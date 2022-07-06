import asyncio
from typing import Any, Mapping, Sequence

import mongomock_motor
import pytest

from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1alpha import models_pb2


class MockProtoRepository(
    mixins.AllMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _proto = models_pb2.Place


class MockRepository(
    mixins.AllMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    """Used for tests with various mixins."""

    async def find_subset(
        self,
        identifiers: Sequence[str],
    ) -> resultset.ResultSet[Mapping[str, Any]]:
        return await self._find_with_cursor(
            "",
            {
                "_id": {
                    "$in": identifiers,
                },
            },
        )


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
    assert await documents.cursor() != ""


@pytest.mark.asyncio
async def test_cursor_filters() -> None:
    repo = MockRepository(mongomock_motor.AsyncMongoMockClient()["tests"]["test"])

    await asyncio.gather(
        repo.insert({"_id": "foobar_foobar"}),
    )

    documents = await repo.find_subset(["bazqux_foobar"])
    assert "foobar_foobar" not in {document["_id"] async for document in documents}

    documents = await repo.find_subset(["foobar_foobar"])
    assert "foobar_foobar" in {document["_id"] async for document in documents}


@pytest.mark.asyncio
async def test_proto_repository() -> None:
    payload = models_pb2.Place()
    repo = MockProtoRepository(mongomock_motor.AsyncMongoMockClient()["tests"]["test"])
    await repo.insert(payload)

    documents = await repo.all_()
    documents.limit(1)

    async for document in documents:
        assert document.updated_at
