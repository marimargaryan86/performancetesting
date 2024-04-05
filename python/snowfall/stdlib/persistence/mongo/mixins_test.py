from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from _pytest import fixtures  # noqa: WPS436
from motor import motor_asyncio

from snowfall.stdlib.persistence.mongo import mixins, testing


class DefaultRepository(
    testing.DefaultRepository,
    mixins.AllMixin[Mapping[str, Any]],
    mixins.EstimatedCountMixin[Mapping[str, Any]],
    mixins.ExistsMixin[Mapping[str, Any]],
    mixins.FindByIdMixin[Mapping[str, Any]],
    mixins.InsertMixin[Mapping[str, Any]],
    mixins.InsertManyMixin[Mapping[str, Any]],
    mixins.UpsertMixin[Mapping[str, Any]],
):
    """DefaultRepository with mixins."""


class ProtoRepository(
    testing.ProtoRepository,
    mixins.AllMixin[testing.FoobarProto],
    mixins.EstimatedCountMixin[testing.FoobarProto],
    mixins.ExistsMixin[testing.FoobarProto],
    mixins.FindByIdMixin[testing.FoobarProto],
    mixins.InsertMixin[testing.FoobarProto],
    mixins.InsertManyMixin[testing.FoobarProto],
    mixins.UpsertMixin[testing.FoobarProto],
):
    """ProtoRepository with mixins."""


class PydanticRepository(
    testing.PydanticRepository,
    mixins.AllMixin[testing.FoobarModel],
    mixins.EstimatedCountMixin[testing.FoobarModel],
    mixins.ExistsMixin[testing.FoobarModel],
    mixins.FindByIdMixin[testing.FoobarModel],
    mixins.InsertMixin[testing.FoobarModel],
    mixins.InsertManyMixin[testing.FoobarModel],
    mixins.UpsertMixin[testing.FoobarModel],
):
    """PydanticRepository with mixins."""


_AnyRepository = DefaultRepository | ProtoRepository | PydanticRepository
_RepositoryClasses = (
    DefaultRepository,
    ProtoRepository,
    PydanticRepository,
)


@pytest.fixture()
async def mongo_collection(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> motor_asyncio.AsyncIOMotorCollection:
    return mongo_client["foobar"]["default"]


@pytest.fixture()
async def initialized_repository(
    request: fixtures.SubRequest,
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
) -> _AnyRepository:
    return request.param(mongo_collection)


@pytest.mark.parametrize(
    "initialized_repository",
    _RepositoryClasses,
    indirect=["initialized_repository"],
)
async def test_all_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
) -> None:
    assert not (
        len([document async for document in await initialized_repository.all_()])
    )
    await mongo_collection.insert_many([{"_id": "foobar"}, {"_id": "bazqux"}])
    assert (
        len([document async for document in await initialized_repository.all_()]) == 2
    )


@pytest.mark.parametrize(
    "initialized_repository",
    _RepositoryClasses,
    indirect=["initialized_repository"],
)
async def test_estimated_count_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
) -> None:
    assert await initialized_repository.estimated_count() == 0
    await mongo_collection.insert_many([{"_id": "foobar"}, {"_id": "bazqux"}])
    assert await initialized_repository.estimated_count() == 2


@pytest.mark.parametrize(
    "initialized_repository",
    _RepositoryClasses,
    indirect=["initialized_repository"],
)
async def test_exists_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
) -> None:
    assert not await initialized_repository.exists("foobar")
    await mongo_collection.insert_one({"_id": "foobar"})
    assert await initialized_repository.exists("foobar")


@pytest.mark.parametrize(
    "initialized_repository",
    _RepositoryClasses,
    indirect=["initialized_repository"],
)
async def test_find_by_id_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
) -> None:
    assert not await initialized_repository.find_by_id("foobar")
    await mongo_collection.insert_one({"_id": "foobar"})
    assert await initialized_repository.find_by_id("foobar")


@pytest.mark.parametrize(
    ("initialized_repository", "document"),
    zip(
        _RepositoryClasses,
        (
            {"_id": "foobar"},
            testing.FoobarProto(id="foobar"),
            testing.FoobarModel(id="foobar"),
        ),
        strict=True,
    ),
    indirect=["initialized_repository"],
)
async def test_insert_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
    document: Any,
) -> None:
    assert not await mongo_collection.find_one({"_id": "foobar"})
    await initialized_repository.insert(document)
    assert await mongo_collection.find_one({"_id": "foobar"})


@pytest.mark.parametrize(
    ("initialized_repository", "documents"),
    zip(
        _RepositoryClasses,
        (
            ({"_id": "foobar"}, {"_id": "bazqux"}),
            (testing.FoobarProto(id="foobar"), testing.FoobarProto(id="bazqux")),
            (testing.FoobarModel(id="foobar"), testing.FoobarModel(id="bazqux")),
        ),
        strict=True,
    ),
    indirect=["initialized_repository"],
)
async def test_insert_many_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
    documents: Sequence[Any],
) -> None:
    assert not len([
        document
        async for document in mongo_collection.find({
            "_id": {"$in": ["foobar", "bazqux"]},
        })
    ])
    await initialized_repository.insert_many(documents)
    assert (
        len([
            document
            async for document in mongo_collection.find({
                "_id": {"$in": ["foobar", "bazqux"]},
            })
        ])
        == 2
    )


@pytest.mark.parametrize(
    ("initialized_repository", "document"),
    zip(
        _RepositoryClasses,
        (
            {"_id": "foobar", "read_only": "foobar"},
            testing.FoobarProto(id="foobar", read_only="foobar"),
            testing.FoobarModel(id="foobar", read_only="foobar"),
        ),
        strict=True,
    ),
    indirect=["initialized_repository"],
)
async def test_upsert_mixin(
    mongo_collection: motor_asyncio.AsyncIOMotorCollection,
    initialized_repository: _AnyRepository,
    document: Any,
) -> None:
    await mongo_collection.insert_one({"_id": "foobar"})
    record = await mongo_collection.find_one({"_id": "foobar"})
    assert record
    assert not record.get("read_only")
    await initialized_repository.upsert(document)
    record = await mongo_collection.find_one({"_id": "foobar"})
    assert record
    assert record.get("read_only") == "foobar"
