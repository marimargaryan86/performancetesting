import pymongo
from pymongo.errors import PyMongoError

from snowfall.project.junction.plus.service.orders_registration.v1alpha import (
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import repository


class OrderRepository(repository.ProtoRepository[models_pb2.PersistedOrder]):
    _proto = models_pb2.PersistedOrder
    _nested_path = "bookings"
    _indexes = [
        pymongo.IndexModel("subscriber_id", background=True),
        pymongo.IndexModel("bookings.route_identifier", background=True),
    ]

    async def create(
        self,
        order: models_pb2.IncomingOrder,
        subscriber: models_pb2.Subscriber,
    ) -> models_pb2.PersistedOrder:
        persisted_order = models_pb2.PersistedOrder(
            id=string.uuid(),
            subscriber_id=subscriber.id,
            reseller_id=order.reseller_id,
            external_ref_id=order.external_ref_id,
            passengers=order.passengers,
            bookings=order.bookings,
        )
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(persisted_order),
        )

        if not insert.acknowledged:
            raise PyMongoError("Insert was not acknowledged")

        return persisted_order


class SubscriberRepository(repository.ProtoRepository[models_pb2.Subscriber]):
    _proto = models_pb2.Subscriber
    _indexes = [
        pymongo.IndexModel("email", background=True),
        pymongo.IndexModel("phone_number", background=True),
        pymongo.IndexModel("reseller_id", background=True),
    ]

    async def get_or_create(
        self,
        order: models_pb2.IncomingOrder,
    ) -> models_pb2.Subscriber:
        subscriber = await self._execute(
            self._collection.find_one,
            filter={
                "reseller_id": order.reseller_id,
                "phone_number.e164_number": order.contact_details.phone.e164_number,
                "email": order.contact_details.email,
            },
        )

        if subscriber:
            return subscriber

        subscriber = models_pb2.Subscriber(
            id=string.uuid(),
            reseller_id=order.reseller_id,
            phone_number=order.contact_details.phone,
            email=order.contact_details.email,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(subscriber),
        )

        if not insert.acknowledged:
            raise PyMongoError("Insert was not acknowledged")

        return subscriber
