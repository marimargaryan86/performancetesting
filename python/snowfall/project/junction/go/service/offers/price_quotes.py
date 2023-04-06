import datetime
from typing import Sequence

import pymongo
from motor import motor_asyncio

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository


class PriceQuoteContainerRepository(
    mixins.FindByIdMixin[models_pb2.PriceQuoteContainer],
    mixins.InsertMixin[models_pb2.PriceQuoteContainer],
    repository.ProtoRepository[models_pb2.PriceQuoteContainer],
):
    _proto = models_pb2.PriceQuoteContainer
    _indexes = [
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    ]

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ):
        super().__init__(collection)
        self._ttl = ttl

    async def create(
        self,
        offer_id: str,
        option_ids: Sequence[str],
        session_token: str,
    ) -> models_pb2.PriceQuoteContainer:
        price_quote = models_pb2.PriceQuoteContainer(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
            ),
            offer_id=offer_id,
            option_ids=option_ids,
            session_token=session_token,
        )

        return await self.insert(price_quote)


class PriceQuoteRepository(
    repository.ProtoRepository[models_pb2.PriceQuote],
    mixins.FindByIdMixin[models_pb2.PriceQuote],
):
    _proto = models_pb2.PriceQuote
    _indexes = [
        pymongo.IndexModel("quotes._id", background=True),
    ]

    async def add_to_container(
        self,
        price_quote_container_id: str,
        price_quote: models_pb2.PriceQuote,
    ) -> models_pb2.PriceQuote:
        update = await self._execute(
            self._collection.update_one,
            filter={"_id": price_quote_container_id},
            update={
                "$push": {
                    "quotes": self._coder.encode(price_quote),
                },
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return price_quote
