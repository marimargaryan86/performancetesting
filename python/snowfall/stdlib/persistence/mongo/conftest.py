import asyncio
import datetime
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
    _indexes = (pymongo.IndexModel("field"), pymongo.IndexModel("created"))

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
    _indexes = (
        pymongo.IndexModel("nested._id"),
        pymongo.IndexModel("nested.field"),
        pymongo.IndexModel("nested.created"),
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


@pytest.fixture()
def nested_mock_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> NestedMockRepository:
    return NestedMockRepository(mongo_client.test.test)


@pytest.fixture()
def mock_db_values() -> list[dict[str, Any]]:
    now = datetime.datetime.now(tz=datetime.UTC)

    return [
        {"_id": "2", "field": "A", "created": now - datetime.timedelta(hours=3)},
        {"_id": "1", "field": "B", "created": now - datetime.timedelta(hours=4)},
        {"_id": "3", "field": "C", "created": now - datetime.timedelta(hours=2)},
        {"_id": "4", "field": "A", "created": now - datetime.timedelta(hours=1)},
    ]


@pytest.fixture()
async def sorting_repository(
    mock_repository: MockRepository,
    mock_db_values: Sequence[Mapping[str, Any]],
) -> MockRepository:
    await asyncio.gather(
        *[mock_repository.insert(dict(db_value)) for db_value in mock_db_values],
    )

    return mock_repository


@pytest.fixture()
async def nested_sorting_repository(
    nested_mock_repository: NestedMockRepository,
    mock_db_values: Sequence[Mapping[str, Any]],
) -> NestedMockRepository:
    await asyncio.gather(
        nested_mock_repository.insert(
            {
                "nested": [
                    mock_db_values[0],
                    mock_db_values[1],
                ],
            },
        ),
        nested_mock_repository.insert(
            {
                "nested": [
                    mock_db_values[2],
                    mock_db_values[3],
                ],
            },
        ),
    )

    return nested_mock_repository
