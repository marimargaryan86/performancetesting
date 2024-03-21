import uuid

import pytest
from mongomock_motor import MongoClient

from snowfall.project.junction.rocket.service.api.models import AirSearchResult
from snowfall.project.junction.rocket.service.api.repositories import AirSearchRepo

RESULT_UUID = "621f61c0-1605-471a-85f6-f930c8d29cb3"


@pytest.fixture()
def mock_mongo_client() -> MongoClient:
    return MongoClient()


@pytest.fixture()
def air_search_repo(mock_mongo_client: MongoClient) -> AirSearchRepo:
    return AirSearchRepo(mock_mongo_client)


def test_insert_air_search_result(air_search_repo: AirSearchRepo) -> None:
    test_result = AirSearchResult(id=uuid.UUID(RESULT_UUID))
    air_search_repo.insert(test_result)

    inserted_document = air_search_repo.collection.find_one({"id": RESULT_UUID})
    assert inserted_document is not None
    assert inserted_document["id"] == RESULT_UUID


def test_existance(air_search_repo: AirSearchRepo) -> None:
    assert not air_search_repo.exists_id(RESULT_UUID)

    air_search_repo.collection.insert_one({"id": RESULT_UUID})

    assert air_search_repo.exists_id(RESULT_UUID)


def test_find_by_id_air_search_result(air_search_repo: AirSearchRepo) -> None:
    air_search_repo.collection.insert_one({"id": RESULT_UUID})

    found_result = air_search_repo.find_by_id(RESULT_UUID)
    assert found_result.id == uuid.UUID(RESULT_UUID)


def test_raises_if_no_such_collection(air_search_repo: AirSearchRepo) -> None:
    with pytest.raises(ValueError, match="No result for id:no_such_id"):
        air_search_repo.find_by_id("no_such_id")
