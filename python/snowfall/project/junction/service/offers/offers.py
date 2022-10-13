import copy
import datetime
from typing import Optional, Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.project.junction.service.offers.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1alpha import models_pb2 as common_pb2

_IN = "$in"
_OFFER_SEARCH_ID = "offer_search_id"


class TripOfferRepository(
    mixins.FindByIdMixin[models_pb2.OfferGroup],
    mixins.InsertMixin[models_pb2.OfferGroup],
    repository.ProtoRepository[models_pb2.OfferGroup],
):
    _proto = models_pb2.OfferGroup
    _indexes = [
        pymongo.IndexModel(_OFFER_SEARCH_ID, background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    ]

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
    _indexes = [pymongo.IndexModel("segments._id", background=True)]

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

        return await self._find_nested(
            path="$segments",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_id(self, document_id: str) -> Optional[models_pb2.OfferSegment]:
        details = await self._find_nested(
            path="$segments",
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
    _indexes = [pymongo.IndexModel("offers._id", background=True)]

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

        return await self._find_nested(
            path="$offers",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_id(self, document_id: str) -> Optional[models_pb2.Offer]:
        options = await self._find_nested(
            path="$offers",
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
    _indexes = [
        pymongo.IndexModel("offers.segment_details._id", background=True),
        pymongo.IndexModel("offers.segment_details.cabin_class.type", background=True),
    ]

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

        return await self._find_nested(
            path="$offers.segment_details",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_id(
        self,
        document_id: str,
    ) -> Optional[models_pb2.OfferSegmentDetails]:
        details = await self._find_nested(
            path="$offers.segment_details",
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
    mixins.FindByIdMixin[models_pb2.OfferAggregateMapping],
    mixins.InsertMixin[models_pb2.OfferAggregateMapping],
    repository.ProtoRepository[models_pb2.OfferAggregateMapping],
):
    _proto = models_pb2.OfferAggregateMapping
    _indexes = [
        pymongo.IndexModel(_OFFER_SEARCH_ID, background=True),
        pymongo.IndexModel("offer_result_ids", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    ]

    async def find_by_offer_search_id(
        self,
        offer_search_id: str,
        cursor: str,
        cabin_classes: Sequence[common_pb2.CabinClass.Type.ValueType],
    ) -> resultset.ResultSet[models_pb2.OfferAggregateMapping]:
        if not cabin_classes:
            return await self._find_with_cursor(
                cur=cursor,
                filter_={_OFFER_SEARCH_ID: offer_search_id},
            )

        filter_pre_cursor = {_OFFER_SEARCH_ID: offer_search_id}
        cursor_filter = copy.deepcopy(dict(filter_pre_cursor))

        if cursor:
            cursor_filter = self._with_cursor_filters(cursor, filter_pre_cursor)

        aggregate = [
            {
                "$match": cursor_filter,
            },
            {
                "$lookup": {
                    "from": "trip_offers",
                    "localField": "offer_result_ids",
                    "foreignField": "_id",
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
            {"$sort": {"_id": 1}},
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
        )


class OfferSearchRepository(  # noqa: WPS215
    mixins.AllMixin[models_pb2.OfferSearch],
    mixins.FindByIdMixin[models_pb2.OfferSearch],
    mixins.InsertMixin[models_pb2.OfferSearch],
    repository.ProtoRepository[models_pb2.OfferSearch],
):
    _proto = models_pb2.OfferSearch
    _indexes = [pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True)]

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ):
        super().__init__(collection)
        self._ttl = ttl

    async def create(
        self,
        document: models_pb2.OfferSearch,
    ) -> models_pb2.OfferSearch:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )
        offer_search = models_pb2.OfferSearch(
            id=string.uuid(),
            expires_at=expires_at,
            trip=document.trip,
        )

        return await self.insert(offer_search)
