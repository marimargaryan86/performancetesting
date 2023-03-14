from __future__ import annotations

import datetime
from typing import Any, Sequence

import pymongo

from snowfall.project.junction.adapter import (
    passenger_name_records as passenger_name_records_adapter,
)
from snowfall.project.junction.service.orders.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1alpha import postal_address_pb2


class JourneyRepository(
    mixins.FindByIdMixin[models_pb2.Journey],
    repository.ProtoRepository[models_pb2.Journey],
):
    _proto = models_pb2.Journey

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
        contact_details: models_pb2.ContactDetails,
    ) -> models_pb2.Journey:
        journey = models_pb2.Journey(
            id=string.uuid(),
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
    ) -> resultset.ResultSet[models_pb2.Journey]:
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


class OrderRepository(repository.ProtoRepository[models_pb2.Order]):
    _proto = models_pb2.Order
    _indexes = [
        pymongo.IndexModel("orders._id", background=True),
        pymongo.IndexModel("orders.journey_id", background=True),
    ]

    async def create_from_options(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
        residence_address: postal_address_pb2.PostalAddress | None,
    ) -> models_pb2.Order:
        order_id = string.uuid()
        order = models_pb2.Order(
            id=order_id,
            journey_id=journey_id,
            passengers=passengers,
            bookings=self._generate_bookings(order_id, options),
            residence_address=residence_address,
        )
        update = await self._execute(
            self._collection.update_one,
            filter={"_id": journey_id},
            update={
                "$push": {
                    "orders": self._coder.encode(order),
                },
                "$set": {"updated_at": datetime.datetime.now(tz=datetime.timezone.utc)},
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return order

    async def find_by_id(
        self,
        document_id: str,
    ) -> models_pb2.Order | None:
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
    ) -> resultset.ResultSet[models_pb2.Order]:
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
    ) -> resultset.ResultSet[models_pb2.Order]:
        return await self._find_nested(
            path="$orders",
            cur=cursor,
            filter_={
                "orders.journey_id": {
                    "$eq": journey_id,
                },
            },
        )

    def _generate_bookings(
        self,
        order_id: str,
        options: Sequence[models_pb2.TripOption],
    ) -> list[models_pb2.Booking]:
        bookings = []
        now = protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.timezone.utc),
        )

        for option in options:
            booking_id = string.uuid()
            self._generate_option_ids(booking_id, option)

            bookings.append(
                models_pb2.Booking(
                    id=booking_id,
                    order_id=order_id,
                    total_price=option.price,
                    trip_option=option,
                    status=models_pb2.Booking.Status.STATUS_PENDING,
                    created_at=now,
                    updated_at=now,
                ),
            )

        return bookings

    def _generate_option_ids(
        self,
        booking_id: str,
        option: models_pb2.TripOption,
    ) -> None:
        option.booking_id = booking_id

        for detail in option.details:
            detail.id = string.uuid()
            detail.booking_id = booking_id


class BookingRepository(repository.ProtoRepository[models_pb2.Booking]):
    _proto = models_pb2.Booking
    _indexes = [
        pymongo.IndexModel("orders.bookings._id", background=True),
        pymongo.IndexModel("orders.bookings.order_id", background=True),
    ]

    async def find_by_id(
        self,
        document_id: str,
    ) -> models_pb2.Booking | None:
        bookings = await self._find_nested(
            path="$orders.bookings",
            filter_={
                "orders.bookings._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await bookings.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Booking]:
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
    ) -> resultset.ResultSet[models_pb2.Booking]:
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
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        await self._execute(
            self._collection.update_one,
            filter={"orders.bookings._id": booking.id},
            update={
                "$set": {
                    "orders.$[order].bookings.$[booking]": self._coder.encode(booking),
                    "orders.$[order].updated_at": now,
                    "updated_at": now,
                },
            },
            array_filters=[
                {
                    "order._id": booking.order_id,
                },
                {
                    "booking._id": booking.id,
                },
            ],
        )

        return booking


class BookingDetailsRepository(
    repository.ProtoRepository[models_pb2.TripOptionDetails],
):
    _proto = models_pb2.TripOptionDetails
    _indexes = [
        pymongo.IndexModel("orders.bookings.trip_option._id", background=True),
        pymongo.IndexModel("orders.bookings.trip_option.details._id", background=True),
    ]

    async def find_by_id(
        self,
        document_id: str,
    ) -> models_pb2.TripOptionDetails | None:
        options = await self._find_nested(
            path="$orders.bookings.trip_option.details",
            filter_={
                "orders.bookings.trip_option.details._id": {
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
    ) -> resultset.ResultSet[models_pb2.TripOptionDetails]:
        filter_ = (
            {
                "orders.bookings.trip_option.details._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_nested(
            path="$orders.bookings.trip_option.details",
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_booking_id(
        self,
        booking_id: str,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.TripOptionDetails]:
        return await self._find_nested(
            path="$orders.bookings.trip_option.details",
            cur=cursor,
            filter_={
                "orders.bookings.trip_option.details.booking_id": {
                    "$eq": booking_id,
                },
            },
        )
