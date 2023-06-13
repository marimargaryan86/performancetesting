import asyncio
from collections.abc import Mapping, Sequence
from typing import Any

import pymongo
import pytest
from motor import motor_asyncio

from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import testing_pb2


class FoobarRepository(
    mixins.AllMixin[testing_pb2.Foobar],
    mixins.InsertMixin[testing_pb2.Foobar],
    repository.ProtoRepository[testing_pb2.Foobar],
):
    _nested_path = "foobars"
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

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )


class MockRepository(
    mixins.AllMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    _indexes = [pymongo.IndexModel("field")]

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


class NestedMockRepository(
    mixins.AllMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    _nested_path = "nested"
    _indexes = [
        pymongo.IndexModel("nested._id"),
        pymongo.IndexModel("nested.field"),
    ]


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


@pytest.fixture()
def nested_mock_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> NestedMockRepository:
    return NestedMockRepository(mongo_client.test.test)


@pytest.fixture()
async def sorting_repository(
    mock_repository: MockRepository,
) -> MockRepository:
    await asyncio.gather(
        mock_repository.insert({"_id": "2", "field": "A"}),
        mock_repository.insert({"_id": "1", "field": "B"}),
        mock_repository.insert({"_id": "3", "field": "C"}),
        mock_repository.insert({"_id": "4", "field": "A"}),
    )

    return mock_repository


@pytest.fixture()
async def nested_sorting_repository(
    nested_mock_repository: NestedMockRepository,
) -> NestedMockRepository:
    await asyncio.gather(
        nested_mock_repository.insert(
            {
                "nested": [
                    {"_id": "2", "field": "A"},
                    {"_id": "1", "field": "B"},
                ],
            },
        ),
        nested_mock_repository.insert(
            {
                "nested": [
                    {"_id": "3", "field": "C"},
                    {"_id": "4", "field": "A"},
                ],
            },
        ),
    )

    return nested_mock_repository
