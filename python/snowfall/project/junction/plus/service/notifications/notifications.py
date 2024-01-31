import copy
import datetime
import json
from collections.abc import Sequence

import pymongo

from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import datetime_pb2
from snowfall.vendor.consul.client import ConsulClient


class OrderRepository(
    repository.ProtoRepository[models_pb2.PersistedOrder],
    mixins.FindByIdMixin[models_pb2.PersistedOrder],
):
    _proto = models_pb2.PersistedOrder
    _nested_path = "bookings"
    _indexes = (
        pymongo.IndexModel("subscriber_id", background=True),
        pymongo.IndexModel("bookings.route_identifier", background=True),
    )

    async def create(
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

    async def find(
        self,
        identifier: str,
        selector: str,
    ) -> resultset.ResultSet[models_pb2.PersistedOrder]:
        return await self._execute(
            self._collection.find,
            {selector: identifier},
        )


class SubscriberRepository(
    repository.ProtoRepository[models_pb2.Subscriber],
    mixins.FindByIdMixin[models_pb2.Subscriber],
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
        passenger: models_pb2.Passenger,
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
            first_name=passenger.first_name,
            last_name=passenger.last_name,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(subscriber),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return subscriber

    async def create_for_cv(self, reseller_id: str) -> models_pb2.Subscriber:
        subscriber = models_pb2.Subscriber(
            id=reseller_id,
            reseller_id=reseller_id,
            webhook_endpoint=models_pb2.WebhookEndpoint(
                encryption_key=string.uuid().replace("-", ""),
            ),
        )
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(subscriber),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return subscriber

    async def find_by_reseller(
        self,
        reseller_id: str,
        mobile_phone: str,
    ) -> models_pb2.Subscriber | None:
        return await self._execute(
            self._collection.find_one,
            {
                "reseller_id": reseller_id,
                "phone_number.e164_number": mobile_phone,
            },
        )

    async def unsubscribe(self, identifier: str) -> bool:
        update = await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "phone_subscription_status": (
                        models_pb2.Subscriber.SubscribedStatus.SUBSCRIBED_STATUS_UNSUBSCRIBED
                    ),
                },
            },
            upsert=False,
        )

        return update.matched_count

    async def subscribe(self, identifier: str) -> bool:
        update = await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "phone_subscription_status": (
                        models_pb2.Subscriber.SubscribedStatus.SUBSCRIBED_STATUS_SUBSCRIBED
                    ),
                },
            },
            upsert=False,
        )

        return update.matched_count

    async def update_push_notifications_token(
        self,
        reseller_id: str,
        mobile_phone: str,
        token: str,
    ) -> bool:
        update = await self._execute(
            self._collection.update_one,
            {
                "reseller_id": reseller_id,
                "phone_number.e164_number": mobile_phone,
            },
            {
                "$set": {
                    "push_notifications_token": token,
                },
            },
            upsert=False,
        )

        return update.matched_count


class ConfigurationVectorRepository(
    repository.ProtoRepository[models_pb2.ConfigurationVector],
    mixins.FindByIdMixin[models_pb2.ConfigurationVector],
    mixins.InsertMixin[models_pb2.ConfigurationVector],
):
    _proto = models_pb2.ConfigurationVector
    _indexes = (pymongo.IndexModel("reseller_id", background=True),)

    async def find_by_selector(
        self,
        selection_value: str,
        selector: str,
    ) -> models_pb2.ConfigurationVector | None:
        return await self._execute(
            self._collection.find_one,
            {selector: selection_value},
        )

    async def update(
        self,
        configuration_vector: models_pb2.ConfigurationVector,
    ) -> bool:
        replacement = self._coder.encode(configuration_vector)
        replacement.pop(repository.mongo_id_key)

        update: pymongo.results.UpdateResult = await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: configuration_vector.id},
            {"$set": replacement},
            upsert=False,
        )

        if not update.acknowledged:
            raise RuntimeError()

        return update.acknowledged

    async def update_permissions(
        self,
        reseller_id: str,
        permissions_to_add: Sequence[str],
        permissions_to_remove: Sequence[str],
        cv_permissions: dict[str, list[str]],
        consul_client: ConsulClient,
        consul_key: str,
    ) -> bool:
        vector = await self.find_by_selector(reseller_id, "reseller_id")
        if not vector:
            return False

        updated_permissions = set(
            list(set(vector.permissions) - set(permissions_to_remove))
            + list(permissions_to_add),
        )

        update: pymongo.results.UpdateResult = await self._execute(
            self._collection.update_one,
            {"reseller_id": reseller_id},
            {"$set": {"permissions": list(updated_permissions)}},
            upsert=False,
        )

        if not update.acknowledged:
            raise RuntimeError()

        # Update permissions in consul
        cv_permissions_mapping = copy.deepcopy(cv_permissions)
        cv_permissions_mapping[reseller_id] = list(updated_permissions)
        await consul_client.put_key(
            consul_key,
            json.dumps(cv_permissions_mapping).encode(),
        )

        return update.acknowledged


class MonitoringRuleRepository(
    repository.ProtoRepository[models_pb2.MonitoringRule],
    mixins.FindByIdMixin[models_pb2.MonitoringRule],
    mixins.InsertMixin[models_pb2.MonitoringRule],
    mixins.UpsertMixin[models_pb2.MonitoringRule],
):
    _proto = models_pb2.MonitoringRule
    _indexes = (
        pymongo.IndexModel("booking.value.route_identifier", background=True),
        pymongo.IndexModel("booking.value.departure_at", background=True),
    )

    async def find_by_booking(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.MonitoringRule | None:
        return await self._execute(
            self._collection.find_one,
            {
                "booking.value.route_identifier.carrier": (
                    booking.value.route_identifier.carrier
                ),
                "booking.value.route_identifier.flight_number": (
                    booking.value.route_identifier.flight_number
                ),
                "booking.value.departure_at": protobuf.protobuf_to_datetime(
                    booking.value.departure_at,
                ),
            },
        )

    async def find_rules_for_upcoming_events(
        self,
        departure_after: datetime_pb2.DateTime,
        sent_flag: str,
    ) -> resultset.ResultSet[models_pb2.MonitoringRule]:
        return await self._execute(
            self._collection.find,
            {
                "booking.value.departure_at": {
                    "$gt": protobuf.protobuf_to_datetime(departure_after),
                },
                sent_flag: {"$exists": False},
            },
        )

    async def update_checkin_reminder(self, identifier: str) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {"$set": {"sent_checkin_reminder": datetime.datetime.now(tz=datetime.UTC)}},
        )
        return update_result.modified_count != 0

    async def update_weather_report(self, identifier: str) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            {"_id": identifier},
            {"$set": {"sent_weather_report": datetime.datetime.now(tz=datetime.UTC)}},
        )
        return update_result.modified_count != 0
