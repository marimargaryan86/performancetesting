from __future__ import annotations

import datetime
import re
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any, cast

import grpc
import pymongo

from snowfall.project.junction.go.adapter import (
    passenger_name_records as passenger_name_records_adapter,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
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
        pymongo.IndexModel("created_at", background=True),
        pymongo.IndexModel("updated_at", background=True),
        pymongo.IndexModel("orders.created_at", background=True),
        pymongo.IndexModel("orders.bookings.status", background=True),
        pymongo.IndexModel(
            "orders.bookings.trip_option.details.segment.legs.departure_at",
            name="booking_departure_at",
            background=True,
        ),
        pymongo.IndexModel("orders.passengers.last_name", background=True),
    )

    _journey_filter_field_mapping = MappingProxyType(
        {
            "departure_at": "orders.bookings.trip_option.details.segment.legs.departure_at",
            "booking_status": "orders.bookings.status",
            "order_created_at": "orders.created_at",
            "last_name": "orders.passengers.last_name",
            "passenger_name_record": "passenger_name_record",
        },
    )

    _filter_operator = MappingProxyType(
        {"ge": "$gte", "le": "$lte", "eq": "$eq", "like": "$regex"},
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
        filter_by: Sequence[orders_pb2.ListJourneysRequest.JourneyFilter] | None = None,
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

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        if filter_by:
            filter_ = self._add_journey_filters_to_filter(filter_by, filter_)

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
            sort=sort,
        )

    async def find_by_booking_ids(
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

    def _get_filter_field_and_value(
        self,
        journey_filter: orders_pb2.ListJourneysRequest.JourneyFilter,
    ) -> tuple[str, Any, Any]:
        if journey_filter.HasField("order_created_at"):
            return (
                self._journey_filter_field_mapping["order_created_at"],
                journey_filter.order_created_at.ToDatetime(tzinfo=datetime.UTC),
                None,
            )

        if journey_filter.HasField("departure_at"):
            return (
                self._journey_filter_field_mapping["departure_at"],
                journey_filter.departure_at.ToDatetime(tzinfo=datetime.UTC),
                None,
            )

        if journey_filter.HasField("booking_status"):
            return (
                self._journey_filter_field_mapping["booking_status"],
                journey_filter.booking_status,
                None,
            )

        if journey_filter.HasField("last_name"):
            last_name_filter = re.escape(journey_filter.last_name)
            last_name_filter = "^{last_name}".format(last_name=last_name_filter)
            if len(journey_filter.last_name) < 3:
                last_name_filter = "{last_name}$".format(last_name=last_name_filter)

            return (
                self._journey_filter_field_mapping["last_name"],
                last_name_filter,
                "i",
            )

        if journey_filter.HasField("passenger_name_record"):
            return (
                self._journey_filter_field_mapping["passenger_name_record"],
                journey_filter.passenger_name_record,
                None,
            )

        return ("", None, None)

    def _add_journey_filters_to_filter(
        self,
        filter_by: Sequence[orders_pb2.ListJourneysRequest.JourneyFilter],
        filter_: Mapping[str, Any],
    ) -> dict[str, Any]:
        filter_ = dict(filter_)

        journey_filters = []
        for journey_filter in filter_by:
            filter_field, filter_value, options = self._get_filter_field_and_value(
                journey_filter=journey_filter,
            )

            if filter_field and filter_value:
                filter_query = {
                    filter_field: {
                        self._filter_operator[journey_filter.operator]: filter_value,
                    },
                }
                if options:
                    filter_query[filter_field]["$options"] = options

                journey_filters.append(filter_query)

        if journey_filters:
            filter_["$and"] = journey_filters

        return filter_


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
        pymongo.IndexModel("orders.bookings.transaction_id", background=True),
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
        ids: Sequence[str] | None = None,
        transaction_ids: Sequence[str] | None = None,
        cursor: str = "",
        reseller_id: str = "",
        filter_by_departure_dates: Sequence[str] = (),
    ) -> resultset.ResultSet[models_pb2.Booking]:
        filter_ = {}
        if ids:
            filter_ = {
                "orders.bookings._id": {
                    "$in": ids,
                },
            }
        elif transaction_ids:
            filter_ = {
                "orders.bookings.transaction_id": {
                    "$in": transaction_ids,
                },
            }

        if filter_by_departure_dates:
            departure_dates = [
                datetime.datetime.strptime(departure_date, "%Y-%m-%d").astimezone(
                    datetime.UTC,
                )
                for departure_date in filter_by_departure_dates
            ]
            filter_departure_dates = [
                {
                    "orders.bookings.trip_option.details.segment.legs.departure_at": {
                        "$gte": departure_date,
                        "$lt": departure_date + datetime.timedelta(days=1),
                    },
                }
                for departure_date in departure_dates
            ]
            filter_["$or"] = filter_departure_dates  # type: ignore[assignment]

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
        pymongo.IndexModel(
            "orders.bookings.trip_option.details.segment.legs.departure_at",
            background=True,
            name="booking_departure_at",
        ),
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
            sort=(
                "segment.legs.departure_at",
                pymongo.ASCENDING,
            ),
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

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.CancellationRequest | None:
        return await self._execute(
            self._collection.find_one,
            _add_reseller_id_to_filter(reseller_id, {"_id": document_id}),
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

    async def find_by_ticket_id(
        self,
        ticket_id: str,
    ) -> models_pb2.CancellationRequest | None:
        filter_ = (
            {
                "booking_cancellations.ticket_id": {
                    "$eq": ticket_id,
                },
            }
            if ticket_id
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


class BookingCancellationsRepository(
    repository.ProtoRepository[models_pb2.BookingCancellation],
):
    _proto = models_pb2.BookingCancellation
    _nested_path = "booking_cancellations"
    _indexes = (
        pymongo.IndexModel("booking_cancellations._id", background=True),
        pymongo.IndexModel("booking_cancellations.booking_id", background=True),
    )

    async def find(
        self,
        ids: Sequence[str],
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.BookingCancellation]:
        return await self._find(ids=ids, reseller_id=reseller_id)

    async def find_by_booking_ids(
        self,
        booking_ids: Sequence[str],
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.BookingCancellation]:
        return await self._find(
            ids=booking_ids,
            reseller_id=reseller_id,
            selector="booking_id",
        )

    async def find_by_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.BookingCancellation | None:
        filter_ = {
            "booking_cancellations._id": {
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

    async def find_by_booking_id(
        self,
        document_id: str,
        reseller_id: str = "",
    ) -> models_pb2.BookingCancellation | None:
        filter_ = {
            "booking_cancellations.booking_id": {
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

    async def update(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> models_pb2.BookingCancellation:
        await self._execute(
            self._collection.update_one,
            filter={"booking_cancellations._id": booking_cancellation.id},
            update={
                "$set": {
                    "booking_cancellations.$[bookingCancellation]": self._coder.encode(
                        booking_cancellation,
                    ),
                },
            },
            array_filters=[
                {
                    "bookingCancellation._id": booking_cancellation.id,
                },
            ],
        )

        return booking_cancellation

    async def _find(
        self,
        ids: Sequence[str],
        reseller_id: str = "",
        selector: str = "_id",
    ) -> resultset.ResultSet[models_pb2.BookingCancellation]:
        filter_ = (
            {
                "booking_cancellations.{0}".format(selector): {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        return await self._find_with_cursor(
            filter_=filter_,
        )
