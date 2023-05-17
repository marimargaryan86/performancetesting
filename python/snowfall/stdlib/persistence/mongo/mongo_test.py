import asyncio

from snowfall.stdlib.persistence.mongo import conftest, resultset
from snowfall.stdlib.v1 import testing_pb2


async def test_result_set(mock_repository: conftest.MockRepository) -> None:
    await asyncio.gather(
        mock_repository.insert({"_id": "foobar_foobar"}),
        mock_repository.insert({"_id": "bazqux_foobar"}),
        mock_repository.insert({"_id": "foobar_bazqux"}),
        mock_repository.insert({"_id": "bazqux_bazqux"}),
    )

    documents = await mock_repository.all_()

    documents.limit(3)

    assert len([document async for document in documents]) == 3

    cursor = await documents.cursor()

    assert cursor != ""

    documents = await mock_repository.all_(cursor=cursor)

    assert isinstance(documents, resultset.ResultSet)

    documents.limit(3)

    assert len([document async for document in documents]) == 1
    assert await documents.cursor() != ""


async def test_cursor_filters(mock_repository: conftest.MockRepository) -> None:
    await asyncio.gather(
        mock_repository.insert({"_id": "foobar_foobar"}),
    )

    documents = await mock_repository.find_subset(["bazqux_foobar"])
    assert "foobar_foobar" not in {document["_id"] async for document in documents}

    documents = await mock_repository.find_subset(["foobar_foobar"])
    assert "foobar_foobar" in {document["_id"] async for document in documents}


async def test_proto_repository(
    foobar_repository: conftest.FoobarRepository,
) -> None:
    payload = testing_pb2.Foobar()
    await foobar_repository.insert(payload)

    documents = await foobar_repository.all_()
    documents.limit(1)

    async for document in documents:
        assert document.updated_at.ToSeconds() > 0
