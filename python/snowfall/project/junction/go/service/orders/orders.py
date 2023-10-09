from __future__ import annotations

import datetime
from collections.abc import Mapping, Sequence
from typing import Any, cast

import grpc
import pymongo

from snowfall.project.junction.go.adapter import (
    passenger_name_records as passenger_name_records_adapter,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.go.service.resellers.v1 import (
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import postal_address_pb2


def _add_reseller_id_to_filter(
    reseller_id: str,
    filter_: Mapping[str, Any],
) -> dict[str, Any]:
    filter_ = dict(filter_)

    if reseller_id:
        filter_["$or"] = [
            {"reseller_id": reseller_id},
            {"owner_reseller_ids": {"$in": [reseller_id]}},
        ]

    return filter_


class JourneyRepository(repository.ProtoRepository[models_pb2.Journey]):
    _proto = models_pb2.Journey
    _indexes = (
        pymongo.IndexModel("passenger_name_record", background=True),
        pymongo.IndexModel("reseller_id", background=True),
        pymongo.IndexModel("owner_reseller_ids", background=True),
    )

    def __init__(
        self,
        *args: Any,
        passenger_name_records: passenger_name_records_adapter.Client,
        resellers_client: resellers_pb2_grpc.ResellerServiceStub,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._passenger_name_records = passenger_name_records
        self._resellers = resellers_client

    async def create(
        self,
        contact_details: models_pb2.ContactDetails,
        reseller_id: str,
    ) -> models_pb2.Journey:
        journey = models_pb2.Journey(
            id=string.uuid(),
            passenger_name_record=(await self._passenger_name_records.create()).id,
            contact_details=contact_details,
            reseller_id=reseller_id,
            owner_reseller_ids=await self._get_journey_owners(reseller_id),
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(journey),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return journey

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.Journey | None:
        return await self._execute(
            self._collection.find_one,
            _add_reseller_id_to_filter(reseller_id, {"_id": document_id}),
        )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
        sort: tuple[str, int] | None = None,
        reseller_id: str = "",
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

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)  # noqa: WPS204

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
            sort=sort,
        )

    async def find_by_booking_id(
        self,
        ids: Sequence[str],
    ) -> resultset.ResultSet[models_pb2.Journey]:
        filter_ = (
            {
                "orders.bookings._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur="",
            filter_=filter_,
        )

    async def _get_journey_owners(self, reseller_id: str) -> list[str]:
        try:
            # Cast Any to expected response type, we ignore gRPC in Mypy.
            response = cast(
                resellers_pb2.GetResellerResponse,
                await self._resellers.GetReseller(
                    resellers_pb2.GetResellerRequest(id=reseller_id),
                ),
            )
        except grpc.aio.AioRpcError:
            return [reseller_id]

        return [reseller_id, *response.reseller.parent_reseller_ids]


class OrderRepository(repository.ProtoRepository[models_pb2.Order]):
    _proto = models_pb2.Order
    _nested_path = "orders"
    _indexes = (
        pymongo.IndexModel("orders._id", background=True),
        pymongo.IndexModel("orders.journey_id", background=True),
    )

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
            filter={repository.mongo_id_key: journey_id},
            update={
                "$push": {
                    "orders": self._coder.encode(order),
                },
                "$set": {"updated_at": datetime.datetime.now(tz=datetime.UTC)},
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return order

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.Order | None:
        filter_ = {
            "orders._id": {
                "$eq": document_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        options = await self._find_with_cursor(
            filter_=filter_,
        )

        try:
            return await options.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
        reseller_id: str = "",
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
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_journey_id(
        self,
        journey_id: str,
        cursor: str,
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.Order]:
        filter_ = {
            "orders.journey_id": {
                "$eq": journey_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    def _generate_bookings(
        self,
        order_id: str,
        options: Sequence[models_pb2.TripOption],
    ) -> list[models_pb2.Booking]:
        bookings = []
        now = protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
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
    _nested_path = "orders.bookings"
    _indexes = (
        pymongo.IndexModel("orders.bookings._id", background=True),
        pymongo.IndexModel("orders.bookings.order_id", background=True),
    )

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.Booking | None:
        filter_ = {
            "orders.bookings._id": {
                "$eq": document_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        bookings = await self._find_with_cursor(
            filter_=filter_,
        )

        try:
            return await bookings.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
        reseller_id: str = "",
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

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_order_id(
        self,
        order_id: str,
        cursor: str,
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.Booking]:
        filter_ = {
            "orders.bookings.order_id": {
                "$eq": order_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def update(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        now = datetime.datetime.now(tz=datetime.UTC)
        booking.updated_at.CopyFrom(protobuf.datetime_to_protobuf(now))

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
    _nested_path = "orders.bookings.trip_option.details"
    _indexes = (
        pymongo.IndexModel("orders.bookings.trip_option._id", background=True),
        pymongo.IndexModel("orders.bookings.trip_option.details._id", background=True),
    )

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.TripOptionDetails | None:
        filter_ = {
            "orders.bookings.trip_option.details._id": {
                "$eq": document_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        options = await self._find_with_cursor(
            filter_=filter_,
        )

        try:
            return await options.take()
        except StopAsyncIteration:
            return None

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
        reseller_id: str = "",
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

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def find_by_booking_id(
        self,
        booking_id: str,
        cursor: str,
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.TripOptionDetails]:
        filter_ = {
            "orders.bookings.trip_option.details.booking_id": {
                "$eq": booking_id,
            },
        }
        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)
        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )


class CancellationRequestsRepository(
    repository.ProtoRepository[models_pb2.CancellationRequest],
    mixins.FindByIdMixin[models_pb2.CancellationRequest],
    mixins.InsertMixin[models_pb2.CancellationRequest],
):
    _proto = models_pb2.CancellationRequest

    async def find_by_booking_ids(
        self,
        ids: Sequence[str],
    ) -> resultset.ResultSet[models_pb2.CancellationRequest]:
        filter_ = (
            {
                "booking_cancellations.booking_id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur="",
            filter_=filter_,
        )

    async def find_by_booking_id(
        self,
        booking_id: str,
    ) -> models_pb2.CancellationRequest | None:
        filter_ = (
            {
                "booking_cancellations.booking_id": {
                    "$eq": booking_id,
                },
            }
            if booking_id
            else {}
        )

        cancellation = await self._find_with_cursor(
            cur="",
            filter_=filter_,
        )

        try:
            return await cancellation.take()
        except StopAsyncIteration:
            return None

    async def find_by_booking_cancellation_id(
        self,
        booking_cancellation_id: str,
    ) -> models_pb2.CancellationRequest | None:
        filter_ = (
            {
                "booking_cancellations._id": {
                    "$eq": booking_cancellation_id,
                },
            }
            if booking_cancellation_id
            else {}
        )

        cancellation = await self._find_with_cursor(
            cur="",
            filter_=filter_,
        )

        try:
            return await cancellation.take()
        except StopAsyncIteration:
            return None

    async def update(
        self,
        document: models_pb2.CancellationRequest,
    ) -> bool:
        replacement = self._coder.encode(document)

        update = await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: replacement[repository.mongo_id_key]},
            replacement=replacement,
        )

        return update.acknowledged
