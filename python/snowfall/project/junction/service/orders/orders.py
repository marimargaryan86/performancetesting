from __future__ import annotations

import uuid
from typing import Any, Optional, Sequence

import pymongo

from snowfall.project.junction.adapter import (
    passenger_name_records as passenger_name_records_adapter,
)
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class JourneyRepository(
    mixins.FindByIdMixin[order_models_pb2.Journey],
    repository.ProtoRepository[order_models_pb2.Journey],
):
    _proto = order_models_pb2.Journey

    def __init__(
        self,
        *args: Any,
        passenger_name_records: passenger_name_records_adapter.Client,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._passenger_name_records = passenger_name_records

    async def create(
        self,
        contact_details: order_models_pb2.ContactDetails,
    ) -> order_models_pb2.Journey:
        journey = order_models_pb2.Journey(
            id=str(uuid.uuid4()),
            passenger_name_record=(await self._passenger_name_records.create()).id,
            contact_details=contact_details,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(journey),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return journey

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Journey]:
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


class OrderRepository(repository.ProtoRepository[order_models_pb2.Order]):
    _proto = order_models_pb2.Order
    _indexes = [
        pymongo.IndexModel("orders._id", background=True),
        pymongo.IndexModel("orders.journey_id", background=True),
    ]

    async def create_from_options(
        self,
        journey_id: str,
        passengers: Sequence[order_models_pb2.Passenger],
        options: Sequence[order_models_pb2.TripOption],
    ) -> order_models_pb2.Order:
        order_id = str(uuid.uuid4())
        order = order_models_pb2.Order(
            id=order_id,
            journey_id=journey_id,
            passengers=passengers,
            bookings=[
                order_models_pb2.Booking(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    trip_option=option,
                    status=order_models_pb2.Booking.Status.STATUS_PENDING,
                )
                for option in options
            ],
        )
        update = await self._execute(
            self._collection.update_one,
            filter={"_id": journey_id},
            update={
                "$push": {
                    "orders": self._coder.encode(order),
                },
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return order

    async def find_by_id(
        self,
        document_id: str,
    ) -> Optional[order_models_pb2.Order]:
        options = await self._find_nested(
            path="$orders",
            filter_={
                "orders._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await options.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Order]:
        filter_ = (
            {
                "orders._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_nested(
            path="$orders",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_journey_id(
        self,
        journey_id: str,
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Order]:
        return await self._find_nested(
            path="$orders",
            cur=cursor,
            filter_={
                "orders.journey_id": {
                    "$eq": journey_id,
                },
            },
        )


class BookingRepository(repository.ProtoRepository[order_models_pb2.Booking]):
    _proto = order_models_pb2.Booking
    _indexes = [
        pymongo.IndexModel("orders.bookings._id", background=True),
        pymongo.IndexModel("orders.bookings.order_id", background=True),
    ]

    async def find_by_id(
        self,
        document_id: str,
    ) -> Optional[order_models_pb2.Booking]:
        options = await self._find_nested(
            path="$orders.bookings",
            filter_={
                "orders.bookings._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await options.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Booking]:
        filter_ = (
            {
                "orders.bookings._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_nested(
            path="$orders.bookings",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_order_id(
        self,
        order_id: str,
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Booking]:
        return await self._find_nested(
            path="$orders.bookings",
            cur=cursor,
            filter_={
                "orders.bookings.order_id": {
                    "$eq": order_id,
                },
            },
        )

    async def update(
        self,
        booking: order_models_pb2.Booking,
    ) -> order_models_pb2.Booking:
        await self._execute(
            self._collection.replace_one,
            filter={"orders.bookings._id": booking.id},
            replacement=self._coder.encode(booking),
        )

        return booking
