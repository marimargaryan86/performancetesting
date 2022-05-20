import datetime
import uuid
from typing import Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.junction.offers.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class TripOfferRepository(
    mixins.InsertMixin[models_pb2.OfferGroup],
    repository.ProtoRepository[models_pb2.OfferGroup],
):
    _proto = models_pb2.OfferGroup
    _indexes = [
        pymongo.IndexModel("offer_search_id", background=True),
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


class OfferAggregateMappingRepository(
    mixins.FindByIdMixin[models_pb2.OfferAggregateMapping],
    mixins.InsertMixin[models_pb2.OfferAggregateMapping],
    repository.ProtoRepository[models_pb2.OfferAggregateMapping],
):
    _proto = models_pb2.OfferAggregateMapping
    _indexes = [
        pymongo.IndexModel("offer_search_id", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    ]

    async def find_by_offer_search_id(
        self,
        offer_search_id: str,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.OfferAggregateMapping]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={"offer_search_id": offer_search_id},
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
            id=str(uuid.uuid4()),
            expires_at=expires_at,
            trip=document.trip,
        )

        return await self.insert(offer_search)
