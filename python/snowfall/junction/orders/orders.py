import datetime

from motor import motor_asyncio

from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.persistence.mongo import repository


class OrderRepository(repository.ProtoRepository[orders_pb2.Order]):
    _proto = orders_pb2.Order

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ):
        super().__init__(collection)
        self._ttl = ttl
