import uuid
from typing import Sequence

from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.stdlib.persistence.mongo import repository


class OrderRepository(repository.ProtoRepository[orders_pb2.Order]):
    _proto = orders_pb2.Order

    async def create(
        self,
        offers: Sequence[offers_pb2.Offer],
    ) -> orders_pb2.Order:
        order = orders_pb2.Order(
            id=str(uuid.uuid4()),
            offers=offers,
        )

        return await self.insert(order)
