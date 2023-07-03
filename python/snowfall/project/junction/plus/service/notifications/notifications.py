from collections.abc import Sequence

import pymongo

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository


class OrderRepository(repository.ProtoRepository[models_pb2.PersistedOrder]):
    _proto = models_pb2.PersistedOrder
    _nested_path = "bookings"
    _indexes = (
        pymongo.IndexModel("subscriber_id", background=True),
        pymongo.IndexModel("bookings.route_identifier", background=True),
    )

    async def create(  # noqa: WPS211
        self,
        reseller_id: str,
        external_ref_id: str,
        booking_reference: str,
        passengers: Sequence[models_pb2.Passenger],
        bookings: Sequence[models_pb2.Booking],
        subscriber: models_pb2.Subscriber,
    ) -> models_pb2.PersistedOrder:
        persisted_order = models_pb2.PersistedOrder(
            id=string.uuid(),
            subscriber_id=subscriber.id,
            reseller_id=reseller_id,
            external_ref_id=external_ref_id,
            booking_reference=booking_reference,
            passengers=passengers,
            bookings=bookings,
        )
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(persisted_order),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return persisted_order


class SubscriberRepository(
    mixins.FindByIdMixin[models_pb2.Subscriber],
    repository.ProtoRepository[models_pb2.Subscriber],
):
    _proto = models_pb2.Subscriber
    _indexes = (
        pymongo.IndexModel("email", background=True),
        pymongo.IndexModel("phone_number", background=True),
        pymongo.IndexModel("reseller_id", background=True),
    )

    async def get_or_create(
        self,
        reseller_id: str,
        contact_details: models_pb2.ContactDetails,
    ) -> models_pb2.Subscriber:
        subscriber = await self._execute(
            self._collection.find_one,
            filter={
                "reseller_id": reseller_id,
                "phone_number.e164_number": contact_details.phone.e164_number,
                "email": contact_details.email,
            },
        )

        if subscriber:
            return subscriber

        subscriber = models_pb2.Subscriber(
            id=string.uuid(),
            reseller_id=reseller_id,
            phone_number=contact_details.phone,
            email=contact_details.email,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(subscriber),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return subscriber


class ConfigurationVectorRepository(
    mixins.FindByIdMixin[models_pb2.ConfigurationVector],
    repository.ProtoRepository[models_pb2.ConfigurationVector],
):
    _proto = models_pb2.ConfigurationVector
    _indexes = (pymongo.IndexModel("reseller_id", background=True),)
