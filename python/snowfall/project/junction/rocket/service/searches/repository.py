import datetime
from collections.abc import Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import core

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import amqp_pb2

_IN = "$in"
_SEARCH_ID = "search_id"


class SearchResultRepository(
    repository.ProtoRepository[models_pb2.SearchResult],
    mixins.FindByIdMixin[models_pb2.SearchResult],
    mixins.InsertMixin[models_pb2.SearchResult],
    mixins.InsertManyMixin[models_pb2.SearchResult],
):
    _proto = models_pb2.SearchResult
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.SearchResult]:
        filter_ = (
            {
                repository.mongo_id_key: {
                    _IN: ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_search_id(
        self,
        search_id: str,
    ) -> resultset.ResultSet[models_pb2.SearchResult]:
        return await self._find_with_cursor(
            filter_={
                "search_id": {
                    "$eq": search_id,
                },
            },
        )


class OfferRepository(
    repository.ProtoRepository[models_pb2.Offer],
):
    _proto = models_pb2.Offer
    _nested_path = "offers"
    _indexes = (pymongo.IndexModel("offers._id", background=True),)

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Offer]:
        filter_ = (
            {
                "offers._id": {
                    _IN: ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_id(self, document_id: str) -> models_pb2.Offer | None:
        options = await self._find_with_cursor(
            filter_={
                "offers._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await options.take()
        except StopAsyncIteration:
            return None


class SearchRepository(
    repository.ProtoRepository[models_pb2.Search],
    mixins.AllMixin[models_pb2.Search],
    mixins.FindByIdMixin[models_pb2.Search],
    mixins.InsertMixin[models_pb2.Search],
    mixins.StatusMixin[models_pb2.Search],
):
    _proto = models_pb2.Search
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: core.AgnosticCollection,
        ttl: datetime.timedelta,
    ):
        super().__init__(collection)
        self._ttl = ttl

    async def create(
        self,
        document: models_pb2.Search,
    ) -> models_pb2.Search:
        search = models_pb2.Search()
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        search.CopyFrom(document)
        search.id = string.uuid()
        search.status = amqp_pb2.Trackable.Status.STATUS_PENDING
        search.expires_at.CopyFrom(expires_at)

        return await self.insert(search)

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Search]:
        filter_ = (
            {
                repository.mongo_id_key: {
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

    async def add_search_result_ids(
        self,
        search_id: str,
        search_result_ids: Sequence[str],
    ) -> models_pb2.Search:
        return await self._execute(
            self._collection.update_one,
            filter={"_id": search_id},
            update={"$set": {"search_result_ids": search_result_ids}},
        )


class QuoteRepository(
    repository.ProtoRepository[models_pb2.Quote],
    mixins.FindByIdMixin[models_pb2.Quote],
    mixins.InsertMixin[models_pb2.Quote],
    mixins.UpsertMixin[models_pb2.Quote],
):
    _default_ttl_minutes = 15
    _proto = models_pb2.Quote
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: core.AgnosticCollection,
        ttl: datetime.timedelta | None = None,
    ):
        super().__init__(collection)

        if ttl:
            self._ttl = ttl
        else:
            self._ttl = datetime.timedelta(minutes=self._default_ttl_minutes)

    async def create(
        self,
        offer_id: str,
    ) -> models_pb2.Quote:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        quote = models_pb2.Quote(
            id=string.uuid(),
            offer_id=offer_id,
            expires_at=expires_at,
        )

        return await self.insert(quote)
