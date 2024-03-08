import pymongo

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import repository


class PriceQuoteRepository(repository.ProtoRepository[models_pb2.PriceQuote]):
    _proto = models_pb2.PriceQuote
    _indexes = (pymongo.IndexModel("quotes._id", background=True),)

    async def add_to_container(
        self,
        price_quote_container_id: str,
        price_quote: models_pb2.PriceQuote,
    ) -> models_pb2.PriceQuote:
        update = await self._execute(
            self._collection.update_one,
            filter={repository.mongo_id_key: price_quote_container_id},
            update={
                "$push": {
                    "quotes": self._coder.encode(price_quote),
                },
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return price_quote
