import datetime
import uuid
from typing import Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib.persistence.mongo import repository, resultset


class TripOfferRepository(repository.ProtoRepository[offers_pb2.TripOfferResult]):
    _proto = offers_pb2.TripOfferResult
    _indexes = [pymongo.IndexModel("offer_search_id", background=True)]

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[offers_pb2.TripOfferResult]:
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


class OfferAggregateRepository(repository.ProtoRepository[offers_pb2.OfferAggregate]):
    _proto = offers_pb2.OfferAggregate
    _indexes = [pymongo.IndexModel("offer_search_id", background=True)]

    async def find_by_offer_search_id(
        self,
        offer_search_id: str,
        cursor: str,
    ) -> resultset.ResultSet[offers_pb2.OfferAggregate]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={"offer_search_id": offer_search_id},
        )


class OfferSearchRepository(repository.ProtoRepository[offers_pb2.OfferSearch]):
    _proto = offers_pb2.OfferSearch

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ):
        super().__init__(collection)
        self._ttl = ttl

    async def create(
        self,
        document: offers_pb2.OfferSearch,
    ) -> offers_pb2.OfferSearch:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )
        offer_search = offers_pb2.OfferSearch(
            id=str(uuid.uuid4()),
            expires_at=expires_at,
            trip=document.trip,
        )

        return await self.insert(offer_search)
