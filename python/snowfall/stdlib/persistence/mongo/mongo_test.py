import asyncio
from collections.abc import Sequence

import more_itertools
import pymongo
import pytest

from snowfall.stdlib.persistence import cursor as cursor_module
from snowfall.stdlib.persistence.mongo import conftest, repository, resultset
from snowfall.stdlib.v1 import testing_pb2


async def test_result_set(mock_repository: conftest.MockRepository) -> None:
    await asyncio.gather(
        mock_repository.insert({repository.mongo_id_key: "foobar_foobar"}),
        mock_repository.insert({repository.mongo_id_key: "bazqux_foobar"}),
        mock_repository.insert({repository.mongo_id_key: "foobar_bazqux"}),
        mock_repository.insert({repository.mongo_id_key: "bazqux_bazqux"}),
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


async def test_documents_are_not_duplicated_during_pagination(
    mock_repository: conftest.MockRepository,
) -> None:
    await mock_repository.insert({repository.mongo_id_key: "aaaaa"})

    documents = await mock_repository.all_()

    assert len([doc async for doc in documents]) == 1

    for _ in range(2):
        documents = await mock_repository.all_(cursor=await documents.cursor())
        assert not len([doc async for doc in documents])


async def test_pagination_is_not_reset_on_no_documents(  # noqa: WPS217
    mock_repository: conftest.MockRepository,
) -> None:
    await mock_repository.insert({repository.mongo_id_key: "aaaaa"})

    documents = await mock_repository.all_()
    assert len([doc async for doc in documents]) == 1

    for _ in range(2):
        documents = await mock_repository.all_(await documents.cursor())
        assert not len([doc async for doc in documents])

    await mock_repository.insert({repository.mongo_id_key: "bbbbb"})

    assert (
        len(
            [doc async for doc in await mock_repository.all_(await documents.cursor())],
        )
        == 1
    )


async def test_pagination_with_filter(mock_repository: conftest.MockRepository) -> None:
    identifiers = [str(identifier) for identifier in range(100)]

    for identifier in identifiers:
        await mock_repository.insert(
            {
                repository.mongo_id_key: identifier,
            },
        )

    count = 0
    length = 1
    cursor = ""

    while length:
        documents = await mock_repository.find_subset(
            cursor=cursor,
            identifiers=identifiers,
        )
        documents.limit(1)
        length = len([document async for document in documents])
        count += length
        cursor = await documents.cursor()

    assert count == len(identifiers)


async def test_cursor_filters(mock_repository: conftest.MockRepository) -> None:
    await asyncio.gather(
        mock_repository.insert({repository.mongo_id_key: "foobar_foobar"}),
    )

    documents = await mock_repository.find_subset(["bazqux_foobar"])
    assert "foobar_foobar" not in {
        document[repository.mongo_id_key] async for document in documents
    }

    documents = await mock_repository.find_subset(["foobar_foobar"])
    assert "foobar_foobar" in {
        document[repository.mongo_id_key] async for document in documents
    }


async def test_proto_repository(
    foobar_repository: conftest.FoobarRepository,
) -> None:
    payload = testing_pb2.Foobar()
    await foobar_repository.insert(payload)

    documents = await foobar_repository.all_()
    documents.limit(1)

    async for document in documents:
        assert document.updated_at.ToSeconds() > 0


_TEST_DATA = (
    (None, ["1", "2", "3", "4"]),
    ((repository.mongo_id_key, pymongo.ASCENDING), ["1", "2", "3", "4"]),
    ((repository.mongo_id_key, pymongo.DESCENDING), ["4", "3", "2", "1"]),
    (("field", pymongo.ASCENDING), ["2", "4", "1", "3"]),
    (("field", pymongo.DESCENDING), ["3", "1", "2", "4"]),
    (("created", pymongo.ASCENDING), ["1", "2", "3", "4"]),
    (("created", pymongo.DESCENDING), ["4", "3", "2", "1"]),
)


class TestSorting(object):
    @pytest.mark.parametrize(("sort", "expected"), _TEST_DATA)
    async def test_expected_orders(
        self,
        sorting_repository: conftest.MockRepository,
        sort: tuple[str, int] | None,
        expected: Sequence[str],
    ) -> None:
        documents = await sorting_repository.all_(sort=sort)
        documents.limit(4)
        resolved = [document[repository.mongo_id_key] async for document in documents]
        assert resolved == expected

    async def test_unknown_field_raises_error(
        self,
        sorting_repository: conftest.MockRepository,
    ) -> None:
        with pytest.raises(repository.UnindexedSortFieldError):
            await sorting_repository.all_(
                sort=("unknown", pymongo.ASCENDING),
            )

    async def test_changed_sort_raises_error_during_pagination(
        self,
        sorting_repository: conftest.MockRepository,
    ) -> None:
        documents = await sorting_repository.all_(sort=("field", pymongo.ASCENDING))
        documents.limit(2)
        assert len([document async for document in documents]) == 2
        cursor = await documents.cursor()
        assert cursor != ""

        with pytest.raises(cursor_module.CursorError):
            await sorting_repository.all_(
                cursor=cursor,
                sort=("field", pymongo.DESCENDING),
            )

    @pytest.mark.parametrize(("sort", "expected"), _TEST_DATA)
    @pytest.mark.parametrize(
        "limit",
        [1, 2, 3, 4],
    )
    async def test_pagination(
        self,
        sorting_repository: conftest.MockRepository,
        sort: tuple[str, int] | None,
        limit: int,
        expected: Sequence[str],
    ) -> None:
        cursor = ""

        for subset in more_itertools.chunked(expected, limit):
            documents = await sorting_repository.all_(cursor=cursor, sort=sort)
            documents.limit(limit)
            assert subset == [
                document[repository.mongo_id_key] async for document in documents
            ]
            cursor = await documents.cursor()
            assert cursor != ""


class TestNestedSorting(object):
    @pytest.mark.parametrize(("sort", "expected"), _TEST_DATA)
    async def test_expected_orders(
        self,
        nested_sorting_repository: conftest.NestedMockRepository,
        sort: tuple[str, int] | None,
        expected: Sequence[str],
    ) -> None:
        documents = await nested_sorting_repository.all_(sort=sort)
        documents.limit(4)
        resolved = [document[repository.mongo_id_key] async for document in documents]
        assert resolved == expected

    @pytest.mark.parametrize(("sort", "expected"), _TEST_DATA)
    @pytest.mark.parametrize(
        "limit",
        [1, 2, 3, 4],
    )
    async def test_pagination(
        self,
        nested_sorting_repository: conftest.NestedMockRepository,
        sort: tuple[str, int] | None,
        limit: int,
        expected: Sequence[str],
    ) -> None:
        cursor = ""

        for subset in more_itertools.chunked(expected, limit):
            documents = await nested_sorting_repository.all_(cursor=cursor, sort=sort)
            documents.limit(limit)
            assert subset == [
                document[repository.mongo_id_key] async for document in documents
            ]
            cursor = await documents.cursor()
            assert cursor != ""
