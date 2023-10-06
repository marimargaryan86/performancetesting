import copy
import datetime
from collections.abc import Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import core

from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence import cursor as cursor_module
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import amqp_pb2

_IN = "$in"
_OFFER_SEARCH_ID = "offer_search_id"


class TripOfferRepository(
    repository.ProtoRepository[models_pb2.OfferGroup],
    mixins.FindByIdMixin[models_pb2.OfferGroup],
    mixins.InsertMixin[models_pb2.OfferGroup],
):
    _proto = models_pb2.OfferGroup
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.OfferGroup]:
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


class TripOfferGroupDetailsRepository(
    repository.ProtoRepository[models_pb2.OfferSegment],
):
    _proto = models_pb2.OfferSegment
    _nested_path = "segments"
    _indexes = (pymongo.IndexModel("segments._id", background=True),)

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.OfferSegment]:
        filter_ = (
            {
                "segments._id": {
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

    async def find_by_id(self, document_id: str) -> models_pb2.OfferSegment | None:
        details = await self._find_with_cursor(
            filter_={
                "segments._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await details.take()
        except StopAsyncIteration:
            return None


class OfferOptionsRepository(
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


class OfferOptionDetailsRepository(
    repository.ProtoRepository[models_pb2.OfferSegmentDetails],
):
    _proto = models_pb2.OfferSegmentDetails
    _nested_path = "offers.segment_details"
    _indexes = (
        pymongo.IndexModel("offers.segment_details._id", background=True),
        pymongo.IndexModel("offers.segment_details.cabin_class.type", background=True),
    )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.OfferSegmentDetails]:
        filter_ = (
            {
                "offers.segment_details._id": {
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

    async def find_by_id(
        self,
        document_id: str,
    ) -> models_pb2.OfferSegmentDetails | None:
        details = await self._find_with_cursor(
            filter_={
                "offers.segment_details._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await details.take()
        except StopAsyncIteration:
            return None


class OfferAggregateMappingRepository(
    repository.ProtoRepository[models_pb2.OfferAggregateMapping],
    mixins.FindByIdMixin[models_pb2.OfferAggregateMapping],
    mixins.InsertMixin[models_pb2.OfferAggregateMapping],
):
    _proto = models_pb2.OfferAggregateMapping
    _indexes = (
        pymongo.IndexModel(_OFFER_SEARCH_ID, background=True),
        pymongo.IndexModel("offer_result_ids", background=True),
        pymongo.IndexModel("created_at", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find_by_offer_search_ids(
        self,
        offer_search_ids: Sequence[str],
        cursor: str,
        cabin_classes: Sequence[common_pb2.CabinClass.Type.ValueType],
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[models_pb2.OfferAggregateMapping]:
        if not cabin_classes:
            return await self._find_with_cursor(
                cur=cursor,
                filter_={_OFFER_SEARCH_ID: {"$in": offer_search_ids}},
                sort=sort,
            )

        filter_pre_cursor = {_OFFER_SEARCH_ID: {"$in": offer_search_ids}}
        cursor_filter = copy.deepcopy(dict(filter_pre_cursor))

        if cursor:
            cursor_filter = repository.with_cursor_filters(
                cursor_module.unmarshal(cursor, filter_pre_cursor),
                filter_pre_cursor,
            )

        aggregate = [
            {
                "$match": cursor_filter,
            },
            {
                "$lookup": {
                    "from": "trip_offers",
                    "localField": "offer_result_ids",
                    "foreignField": repository.mongo_id_key,
                    "as": "results",
                },
            },
            {
                "$match": {
                    "results.offers.segment_details.cabin_class.type": {
                        "$in": cabin_classes,
                    },
                },
            },
            {
                "$sort": (
                    {
                        sort[0]: sort[1],
                    }
                    if sort
                    else {repository.mongo_id_key: 1}
                ),
            },
        ]

        return await self._execute(
            query=self._collection.aggregate,
            pipeline=aggregate,
            filter_pre_cursor=filter_pre_cursor,
        )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[models_pb2.OfferAggregateMapping]:
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
            sort=sort,
        )


class OfferSearchRepository(  # noqa: WPS215
    repository.ProtoRepository[models_pb2.OfferSearch],
    mixins.AllMixin[models_pb2.OfferSearch],
    mixins.FindByIdMixin[models_pb2.OfferSearch],
    mixins.InsertMixin[models_pb2.OfferSearch],
    mixins.StatusMixin[models_pb2.OfferSearch],
):
    _proto = models_pb2.OfferSearch
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
        document: models_pb2.OfferSearch,
    ) -> models_pb2.OfferSearch:
        offer_search = models_pb2.OfferSearch()
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        offer_search.CopyFrom(document)
        offer_search.id = string.uuid()
        offer_search.status = amqp_pb2.Trackable.Status.STATUS_PENDING
        offer_search.expires_at.CopyFrom(expires_at)

        return await self.insert(offer_search)

    async def find(
        self,
        ids: Sequence[str],
    ) -> resultset.ResultSet[models_pb2.OfferSearch]:
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
            cur="",
            filter_=filter_,
        )
