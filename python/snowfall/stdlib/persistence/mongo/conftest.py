from typing import Any, Mapping, Sequence

import pytest
from motor import motor_asyncio

from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import testing_pb2


class FoobarRepository(
    mixins.AllMixin[testing_pb2.Foobar],
    mixins.InsertMixin[testing_pb2.Foobar],
    repository.ProtoRepository[testing_pb2.Foobar],
):
    _proto = testing_pb2.Foobar

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[testing_pb2.Foobar]:
        filter_ = (
            {
                "foobars._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_nested(
            path="$foobars",
            cur=cursor,
            filter_=filter_,
        )


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


@pytest.fixture()
def foobar_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> FoobarRepository:
    return FoobarRepository(mongo_client.test.test)


@pytest.fixture()
def mock_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> MockRepository:
    return MockRepository(mongo_client.test.test)
