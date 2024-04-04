import pytest
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.api.air.models import AirSearchResult
from snowfall.project.junction.rocket.service.api.air.repositories import AirSearchRepo

RESULT_UUID = "621f61c0-1605-471a-85f6-f930c8d29cb3"


@pytest.fixture()
async def mock_collection(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> motor_asyncio.AsyncIOMotorCollection:
    return mongo_client["db"]["collection"]


@pytest.fixture()
async def air_search_repo(
    mock_collection: motor_asyncio.AsyncIOMotorCollection,
) -> AirSearchRepo:
    return AirSearchRepo(collection=mock_collection)


async def test_insert_air_search_result(
    air_search_repo: AirSearchRepo,
    mock_collection: motor_asyncio.AsyncIOMotorCollection,
) -> None:
    test_result = AirSearchResult(id=RESULT_UUID, data=[])
    await air_search_repo.insert(test_result)

    inserted_document = await mock_collection.find_one({"id": RESULT_UUID})
    assert inserted_document is not None
    assert inserted_document["id"] == RESULT_UUID


async def test_existence(
    air_search_repo: AirSearchRepo,
    mock_collection: motor_asyncio.AsyncIOMotorCollection,
) -> None:
    assert not await air_search_repo.exists_id(RESULT_UUID)

    await mock_collection.insert_one({"id": RESULT_UUID, "data": []})

    assert await air_search_repo.exists_id(RESULT_UUID)


async def test_find_by_id_air_search_result(
    air_search_repo: AirSearchRepo,
    mock_collection: motor_asyncio.AsyncIOMotorCollection,
) -> None:
    await mock_collection.insert_one({"id": RESULT_UUID, "data": []})

    found_result = await air_search_repo.find_by_id(RESULT_UUID)
    assert found_result.id == RESULT_UUID


async def test_raises_if_no_such_collection(air_search_repo: AirSearchRepo) -> None:
    with pytest.raises(ValueError, match="No result for id:no_such_id"):
        await air_search_repo.find_by_id("no_such_id")
