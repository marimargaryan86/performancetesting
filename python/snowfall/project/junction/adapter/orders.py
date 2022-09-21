from __future__ import annotations

import abc
import uuid
from collections.abc import Iterator
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2,
    orders_pb2,
    orders_pb2_grpc,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.v1alpha import money_pb2

_MOCK_PRICE_UNITS = 13
_MOCK_PRICE_NANOS = 370000000


class NotFoundError(Exception):
    """Raised when an order is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
    ) -> models_pb2.Journey:
        """Create a new journey resource."""

    @abc.abstractmethod
    async def place_order(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
    ) -> models_pb2.Order:
        """Create a new order resource."""

    @abc.abstractmethod
    async def get_journey(self, identifier: str) -> models_pb2.Journey:
        """Fetch a journey resource."""

    @abc.abstractmethod
    async def get_order(self, identifier: str) -> models_pb2.Order:
        """Fetch an order resource."""

    @abc.abstractmethod
    async def get_booking(self, identifier: str) -> models_pb2.Booking:
        """Fetch a booking resource."""

    @abc.abstractmethod
    async def find_journeys(
        self,
        identifiers: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListJourneysResponse:
        """Fetch all journey resources."""

    @abc.abstractmethod
    async def find_orders(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        """Fetch order resources by identifiers."""

    @abc.abstractmethod
    async def find_orders_by_journey_id(
        self,
        journey_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        """Fetch all order resources related to a journey."""

    @abc.abstractmethod
    async def find_bookings(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        """Fetch booking resources by identifiers."""

    @abc.abstractmethod
    async def find_bookings_by_order_id(
        self,
        order_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        """Fetch all booking resources related to a booking."""


class DictClient(Client):
    def __init__(self, journeys: Sequence[models_pb2.Journey]) -> None:
        self._journeys: dict[str, models_pb2.Journey] = {
            journey.id: journey for journey in journeys
        }

    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
    ) -> models_pb2.Journey:
        journey = models_pb2.Journey(
            id=str(uuid.uuid4()),
            passenger_name_record="FOOBAR",
            contact_details=contact_details,
        )
        self._journeys[journey.id] = journey

        return journey

    async def place_order(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
    ) -> models_pb2.Order:
        if journey_id not in self._journeys:
            raise NotFoundError()

        order_id = str(uuid.uuid4())
        order = models_pb2.Order(
            id=order_id,
            journey_id=journey_id,
            bookings=[
                models_pb2.Booking(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    trip_option=option,
                    status=models_pb2.Booking.Status.STATUS_CONFIRMED,
                    provider_name="mock",
                    total_price=money_pb2.Money(
                        currency_code="GBP",
                        units=_MOCK_PRICE_UNITS,
                        nanos=_MOCK_PRICE_NANOS,
                    ),
                    trip_result=models_pb2.TripBooking(
                        record_locator="FOOBAR",
                    ),
                )
                for option in options
            ],
            passengers=passengers,
        )
        self._journeys[journey_id].orders.append(order)

        return order

    async def get_journey(
        self,
        identifier: str,
    ) -> models_pb2.Journey:
        if identifier not in self._journeys:
            raise NotFoundError()

        return self._journeys[identifier]

    async def get_order(self, identifier: str) -> models_pb2.Order:
        for order in self._iterate_orders():
            if identifier == order.id:
                return order

        raise NotFoundError()

    async def get_booking(self, identifier: str) -> models_pb2.Booking:
        for order in self._iterate_orders():
            for booking in order.bookings:
                if identifier == booking.id:
                    return booking

        raise NotFoundError()

    async def find_journeys(
        self,
        identifiers: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListJourneysResponse:
        if identifiers:
            journeys = [
                self._journeys[identifier]
                for identifier in identifiers
                if identifier in self._journeys
            ]
        else:
            journeys = list(self._journeys.values())

        page = sequence.paginate(
            sequence=journeys,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListJourneysResponse(
            journeys=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_orders(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        orders = [order for order in self._iterate_orders() if order.id in identifiers]

        page = sequence.paginate(
            sequence=orders,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListOrdersResponse(
            orders=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_orders_by_journey_id(
        self,
        journey_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        try:
            orders = list(self._journeys[journey_id].orders)
        except KeyError:
            orders = []

        page = sequence.paginate(
            sequence=orders,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListOrdersResponse(
            orders=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_bookings(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        bookings = [
            booking
            for order in self._iterate_orders()
            for booking in order.bookings
            if booking.id in identifiers
        ]

        page = sequence.paginate(
            sequence=bookings,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListBookingsResponse(
            bookings=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_bookings_by_order_id(
        self,
        order_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        bookings = [
            booking
            for order in self._iterate_orders()
            for booking in order.bookings
            if order.id == order_id
        ]

        page = sequence.paginate(
            sequence=bookings,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListBookingsResponse(
            bookings=page.sequence,
            next_page_token=page.cursor,
        )

    def _iterate_orders(self) -> Iterator[models_pb2.Order]:
        for journey in self._journeys.values():
            yield from journey.orders


class GrpcClient(Client):
    def __init__(self, orders: orders_pb2_grpc.OrderServiceStub, timeout: int = 10):
        self._orders = orders
        self._timeout = timeout

    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
    ) -> models_pb2.Journey:
        try:
            response = await self._orders.CreateJourney(
                orders_pb2.CreateJourneyRequest(contact_details=contact_details),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.journey

    async def place_order(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
    ) -> models_pb2.Order:
        try:
            response = await self._orders.PlaceOrder(
                orders_pb2.PlaceOrderRequest(
                    journey_id=journey_id,
                    passengers=passengers,
                    options=[
                        orders_pb2.PlaceOrderRequest.Option(
                            trip_option=option,
                        )
                        for option in options
                    ],
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Journey with ID '{id}' not found.".format(id=journey_id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.order

    async def get_journey(self, identifier: str) -> models_pb2.Journey:
        try:
            response = await self._orders.GetJourney(
                orders_pb2.GetJourneyRequest(id=identifier),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Journey with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.journey

    async def get_order(self, identifier: str) -> models_pb2.Order:
        try:
            response = await self._orders.GetOrder(
                orders_pb2.GetOrderRequest(id=identifier),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Order with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.order

    async def get_booking(self, identifier: str) -> models_pb2.Booking:
        try:
            response = await self._orders.GetBooking(
                orders_pb2.GetBookingRequest(id=identifier),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Booking with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.booking

    async def find_journeys(
        self,
        identifiers: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListJourneysResponse:
        request = orders_pb2.ListJourneysRequest(
            ids=identifiers,
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await self._orders.ListOrders(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

    async def find_orders(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        request = orders_pb2.ListOrdersRequest(
            ids=orders_pb2.ListOfIds(ids=identifiers),
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await self._orders.ListOrders(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

    async def find_orders_by_journey_id(
        self,
        journey_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListOrdersResponse:
        request = orders_pb2.ListOrdersRequest(
            journey_id=journey_id,
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await self._orders.ListOrders(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

    async def find_bookings(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        request = orders_pb2.ListBookingsRequest(
            ids=orders_pb2.ListOfIds(ids=identifiers),
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await self._orders.ListBookings(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

    async def find_bookings_by_order_id(
        self,
        order_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> orders_pb2.ListBookingsResponse:
        request = orders_pb2.ListBookingsRequest(
            order_id=order_id,
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await self._orders.ListBookings(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc
