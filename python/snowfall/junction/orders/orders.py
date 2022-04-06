import uuid
from typing import Sequence

from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class OrderRepository(
    mixins.FindByIdMixin[orders_pb2.Order],
    repository.ProtoRepository[orders_pb2.Order],
):
    _proto = orders_pb2.Order

    async def create_from_offers(
        self,
        offers: Sequence[offers_pb2.Offer],
    ) -> orders_pb2.Order:

        order = orders_pb2.Order(
            id=str(uuid.uuid4()),
            offers=offers,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(order),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return order

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[orders_pb2.Order]:
        return await self._find_with_cursor(
            cur=cursor,
        )
