from __future__ import annotations

import abc
from collections.abc import Iterator, Sequence

from google.protobuf.field_mask_pb2 import FieldMask

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2,
    orders_pb2,
    orders_pb2_grpc,
)
from snowfall.stdlib import sequence, string
from snowfall.stdlib.v1 import postal_address_pb2, sort_pb2

_MOCK_PRICE_UNITS = 13
_MOCK_PRICE_NANOS = 370000000


class Client(abc.ABC):
    @abc.abstractmethod
    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
        reseller_id: str,
    ) -> models_pb2.Journey:
        """Create a new journey resource."""

    @abc.abstractmethod
    async def place_order(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
        residence_address: postal_address_pb2.PostalAddress | None,
    ) -> models_pb2.Order:
        """Create a new order resource."""

    @abc.abstractmethod
    async def get_cancellation_request(
        self,
        identifier: str,
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        """Fetch cancellation request resource."""

    @abc.abstractmethod
    async def find_booking_cancellations(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
    ) -> orders_pb2.ListBookingCancellationsResponse:
        """Fetch booking cancellation resources by identifiers."""

    @abc.abstractmethod
    async def update_booking_cancellations(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> models_pb2.BookingCancellation:
        """Fetch booking cancellation resources by identifiers."""

    @abc.abstractmethod
    async def get_booking_cancellation_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str,
    ) -> models_pb2.BookingCancellation:
        """Fetch booking cancellation resource related to a booking."""

    @abc.abstractmethod
    async def create_cancellation_request(
        self,
        booking_ids: Sequence[str],
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        """Create a new cancellation request resource."""

    @abc.abstractmethod
    async def get_journey(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Journey:
        """Fetch a journey resource."""

    @abc.abstractmethod
    async def get_order(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Order:
        """Fetch an order resource."""

    @abc.abstractmethod
    async def get_booking(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Booking:
        """Fetch a booking resource."""

    @abc.abstractmethod
    async def get_booking_details(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.TripOptionDetails:
        """Fetch a booking details resource."""

    @abc.abstractmethod
    async def find_journeys(
        self,
        identifiers: Sequence[str] | None = None,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        sort_by: sort_pb2.Sort | None = None,
    ) -> orders_pb2.ListJourneysResponse:
        """Fetch all journey resources."""

    @abc.abstractmethod
    async def find_orders(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListOrdersResponse:
        """Fetch order resources by identifiers."""

    @abc.abstractmethod
    async def find_orders_by_journey_id(
        self,
        journey_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListOrdersResponse:
        """Fetch all order resources related to a journey."""

    @abc.abstractmethod
    async def find_bookings(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingsResponse:
        """Fetch booking resources by identifiers."""

    @abc.abstractmethod
    async def find_bookings_by_order_id(
        self,
        order_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingsResponse:
        """Fetch all booking resources related to an order."""

    @abc.abstractmethod
    async def find_booking_details(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        """Fetch booking details resources by identifiers."""

    @abc.abstractmethod
    async def find_booking_details_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        """Fetch all booking details resources related to a booking."""

    @abc.abstractmethod
    async def find_booking_cancellations_for_bookings(
        self,
        bookings: Sequence[models_pb2.Booking],
        reseller_id: str | None = None,
    ) -> list[tuple[models_pb2.Booking, models_pb2.BookingCancellation | None]]:
        """Fetch all booking cancellation resources related to bookings."""

    @abc.abstractmethod
    async def handle_cancellation_ticket_completed(
        self,
        ticket_id: str,
        status: orders_pb2.Status.ValueType,
    ) -> None:
        """Handle cancellation ."""


class DictClient(Client):
    def __init__(
        self,
        journeys: Sequence[models_pb2.Journey],
        booking_cancellations: Sequence[models_pb2.CancellationRequest],
    ) -> None:
        self._journeys: dict[str, models_pb2.Journey] = {
            journey.id: journey for journey in journeys
        }
        self._cancellations: dict[str, models_pb2.CancellationRequest] = {
            cancellation.id: cancellation for cancellation in booking_cancellations
        }

    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
        reseller_id: str,
    ) -> models_pb2.Journey:
        journey = models_pb2.Journey(
            id=string.uuid(),
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
        residence_address: postal_address_pb2.PostalAddress | None,
    ) -> models_pb2.Order:
        if journey_id not in self._journeys:
            raise errors.NotFoundError()

        order_id = string.uuid()
        order = models_pb2.Order(
            id=order_id,
            journey_id=journey_id,
            bookings=self._generate_bookings(order_id, options),
            passengers=passengers,
            residence_address=residence_address,
        )
        self._journeys[journey_id].orders.append(order)

        return order

    async def get_journey(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Journey:
        if identifier not in self._journeys:
            raise errors.NotFoundError()
        return self._journeys[identifier]

    async def get_cancellation_request(
        self,
        identifier: str,
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        if identifier not in self._cancellations:
            raise errors.NotFoundError()

        return self._cancellations[identifier]

    async def find_booking_cancellations(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
    ) -> orders_pb2.ListBookingCancellationsResponse:
        booking_cancellations: list[models_pb2.BookingCancellation] = [
            booking_cancellation
            for cancellations in self._cancellations.values()
            for booking_cancellation in cancellations.booking_cancellations
            if booking_cancellation.id in identifiers
        ]

        return orders_pb2.ListBookingCancellationsResponse(
            booking_cancellations=booking_cancellations,
        )

    async def update_booking_cancellations(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> models_pb2.BookingCancellation:
        return booking_cancellation

    async def get_booking_cancellation_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str,
    ) -> models_pb2.BookingCancellation:
        for cancellations in self._cancellations.values():
            for booking_cancellation in cancellations.booking_cancellations:
                if booking_cancellation.booking_id == booking_id:
                    return booking_cancellation

        raise errors.NotFoundError()

    async def create_cancellation_request(
        self,
        booking_ids: Sequence[str],
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        request = models_pb2.CancellationRequest(
            id=string.uuid(),
            booking_cancellations=[
                models_pb2.BookingCancellation(
                    id=string.uuid(),
                    booking_id=booking_id,
                )
                for booking_id in booking_ids
            ],
            reseller_id=reseller_id,
            status=models_pb2.CancellationRequest.STATUS_PENDING,
        )
        self._cancellations[request.id] = request

        return request

    async def get_order(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Order:
        for order in self._iterate_orders():
            if identifier == order.id:
                return order

        raise errors.NotFoundError()

    async def get_booking(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Booking:
        for booking in self._iterate_bookings():
            if identifier == booking.id:
                return booking

        raise errors.NotFoundError()

    async def get_booking_details(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.TripOptionDetails:
        for booking in self._iterate_bookings():
            for detail in booking.trip_option.details:
                if identifier == detail.id:
                    return detail

        raise errors.NotFoundError()

    async def find_journeys(
        self,
        identifiers: Sequence[str] | None = None,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        sort_by: sort_pb2.Sort | None = None,
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
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
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
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
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
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
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
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
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

    async def find_booking_details(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        details = [
            detail
            for booking in self._iterate_bookings()
            for detail in booking.trip_option.details
            if detail.id in identifiers
        ]

        page = sequence.paginate(
            sequence=details,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListBookingDetailsResponse(
            details=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_booking_details_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        details = [
            detail
            for booking in self._iterate_bookings()
            for detail in booking.trip_option.details
            if booking.id == booking_id
        ]

        page = sequence.paginate(
            sequence=details,
            cursor=cursor,
            limit=limit,
        )

        return orders_pb2.ListBookingDetailsResponse(
            details=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_booking_cancellations_for_bookings(
        self,
        bookings: Sequence[models_pb2.Booking],
        reseller_id: str | None = None,
    ) -> list[tuple[models_pb2.Booking, models_pb2.BookingCancellation | None]]:
        bookings_and_cancellations = []
        for booking in bookings:
            try:
                booking_cancellation = (
                    await self.get_booking_cancellation_by_booking_id(
                        booking.id,
                        reseller_id or "",
                    )
                )
            except errors.NotFoundError:
                booking_cancellation = None

            bookings_and_cancellations.append((booking, booking_cancellation))

        return bookings_and_cancellations

    async def handle_cancellation_ticket_completed(
        self,
        ticket_id: str,
        status: orders_pb2.Status.ValueType,
    ) -> None:
        """Handle cancellation ."""

    def _iterate_orders(self) -> Iterator[models_pb2.Order]:
        for journey in self._journeys.values():
            yield from journey.orders

    def _iterate_bookings(self) -> Iterator[models_pb2.Booking]:
        for order in self._iterate_orders():
            yield from order.bookings

    def _generate_bookings(
        self,
        order_id: str,
        options: Sequence[models_pb2.TripOption],
    ) -> list[models_pb2.Booking]:
        bookings = []

        for option in options:
            booking_id = string.uuid()
            self._generate_option_ids(booking_id, option)

            bookings.append(
                models_pb2.Booking(
                    id=booking_id,
                    order_id=order_id,
                    total_price=option.price,
                    trip_option=option,
                    status=models_pb2.Booking.Status.STATUS_CONFIRMED,
                    trip_result=models_pb2.TripBooking(
                        record_locator="FOOBAR",
                    ),
                ),
            )

        return bookings

    def _generate_option_ids(
        self,
        booking_id: str,
        option: models_pb2.TripOption,
    ) -> None:
        option.id = string.uuid()
        option.booking_id = booking_id

        for detail in option.details:
            detail.id = string.uuid()
            detail.booking_id = booking_id


_GRPC_TIMEOUT_SECONDS = 15


class GrpcClient(Client):
    def __init__(
        self,
        orders: orders_pb2_grpc.OrderServiceStub,
        timeout: int = _GRPC_TIMEOUT_SECONDS,
    ):
        self._orders = orders
        self._timeout = timeout

    async def create_journey(
        self,
        contact_details: models_pb2.ContactDetails,
        reseller_id: str,
    ) -> models_pb2.Journey:
        response = await errors.handle_grpc_errors(
            self._orders.CreateJourney(
                orders_pb2.CreateJourneyRequest(
                    contact_details=contact_details,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.journey

    async def place_order(
        self,
        journey_id: str,
        passengers: Sequence[models_pb2.Passenger],
        options: Sequence[models_pb2.TripOption],
        residence_address: postal_address_pb2.PostalAddress | None,
    ) -> models_pb2.Order:
        response = await errors.handle_grpc_errors(
            self._orders.PlaceOrder(
                orders_pb2.PlaceOrderRequest(
                    journey_id=journey_id,
                    passengers=passengers,
                    residence_address=residence_address,
                    options=[
                        orders_pb2.PlaceOrderRequest.Option(
                            trip_option=option,
                        )
                        for option in options
                    ],
                ),
                timeout=self._timeout,
            ),
        )

        return response.order

    async def get_journey(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Journey:
        response = await errors.handle_grpc_errors(
            self._orders.GetJourney(
                orders_pb2.GetJourneyRequest(
                    id=identifier,
                    reseller_id=reseller_id or "",
                ),
                timeout=self._timeout,
            ),
        )

        return response.journey

    async def get_cancellation_request(
        self,
        identifier: str,
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        response = await errors.handle_grpc_errors(
            self._orders.GetCancellationRequest(
                orders_pb2.GetCancellationRequestRequest(
                    id=identifier,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.cancellation_request

    async def find_booking_cancellations(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
    ) -> orders_pb2.ListBookingCancellationsResponse:
        return await errors.handle_grpc_errors(
            self._orders.ListBookingCancellations(
                orders_pb2.ListBookingCancellationsRequest(
                    ids=orders_pb2.ListOfIds(ids=identifiers),
                    reseller_id=reseller_id or "",
                ),
                timeout=self._timeout,
            ),
        )

    async def update_booking_cancellations(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> models_pb2.BookingCancellation:
        response = await errors.handle_grpc_errors(
            self._orders.UpdateBookingCancellation(
                orders_pb2.UpdateBookingCancellationRequest(
                    booking_cancellation=booking_cancellation,
                    update_mask=FieldMask(
                        paths=[
                            field.name
                            for field in booking_cancellation.DESCRIPTOR.fields
                            if getattr(booking_cancellation, field.name) is not None
                        ],
                    ),
                ),
                timeout=self._timeout,
            ),
        )

        return response.booking_cancellation

    async def get_booking_cancellation_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str,
    ) -> models_pb2.BookingCancellation:
        response = await errors.handle_grpc_errors(
            self._orders.GetBookingCancellation(
                orders_pb2.GetBookingCancellationRequest(
                    booking_id=booking_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.booking_cancellation

    async def create_cancellation_request(
        self,
        booking_ids: Sequence[str],
        reseller_id: str,
    ) -> models_pb2.CancellationRequest:
        response = await errors.handle_grpc_errors(
            self._orders.CreateCancellationRequest(
                orders_pb2.CreateCancellationRequestRequest(
                    cancellation_request=models_pb2.CancellationRequest(
                        id=string.uuid(),
                        booking_cancellations=[
                            models_pb2.BookingCancellation(
                                id=string.uuid(),
                                booking_id=booking_id,
                            )
                            for booking_id in booking_ids
                        ],
                        reseller_id=reseller_id,
                    ),
                ),
                timeout=self._timeout,
            ),
        )

        return response.cancellation_request

    async def get_order(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Order:
        response = await errors.handle_grpc_errors(
            self._orders.GetOrder(
                orders_pb2.GetOrderRequest(
                    id=identifier,
                    reseller_id=reseller_id or "",
                ),
                timeout=self._timeout,
            ),
        )

        return response.order

    async def get_booking(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.Booking:
        response = await errors.handle_grpc_errors(
            self._orders.GetBooking(
                orders_pb2.GetBookingRequest(
                    id=identifier,
                    reseller_id=reseller_id or "",
                ),
                timeout=self._timeout,
            ),
        )

        return response.booking

    async def get_booking_details(
        self,
        identifier: str,
        reseller_id: str | None = None,
    ) -> models_pb2.TripOptionDetails:
        response = await errors.handle_grpc_errors(
            self._orders.GetBookingDetails(
                orders_pb2.GetBookingDetailsRequest(
                    id=identifier,
                    reseller_id=reseller_id or "",
                ),
                timeout=self._timeout,
            ),
        )

        return response.details

    async def find_journeys(
        self,
        identifiers: Sequence[str] | None = None,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        sort_by: sort_pb2.Sort | None = None,
    ) -> orders_pb2.ListJourneysResponse:
        request = orders_pb2.ListJourneysRequest(
            ids=identifiers,
            page_token=cursor or "",
            sort_by=sort_by,
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListJourneys(request, timeout=self._timeout),
        )

    async def find_orders(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListOrdersResponse:
        request = orders_pb2.ListOrdersRequest(
            ids=orders_pb2.ListOfIds(ids=identifiers),
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListOrders(request, timeout=self._timeout),
        )

    async def find_orders_by_journey_id(
        self,
        journey_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListOrdersResponse:
        request = orders_pb2.ListOrdersRequest(
            journey_id=journey_id,
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListOrders(request, timeout=self._timeout),
        )

    async def find_bookings(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingsResponse:
        request = orders_pb2.ListBookingsRequest(
            ids=orders_pb2.ListOfIds(ids=identifiers),
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListBookings(request, timeout=60),
        )

    async def find_bookings_by_order_id(
        self,
        order_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingsResponse:
        request = orders_pb2.ListBookingsRequest(
            order_id=order_id,
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListBookings(request, timeout=self._timeout),
        )

    async def find_booking_details(
        self,
        identifiers: Sequence[str],
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        request = orders_pb2.ListBookingDetailsRequest(
            ids=orders_pb2.ListOfIds(ids=identifiers),
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListBookingDetails(request, timeout=self._timeout),
        )

    async def find_booking_details_by_booking_id(
        self,
        booking_id: str,
        reseller_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> orders_pb2.ListBookingDetailsResponse:
        request = orders_pb2.ListBookingDetailsRequest(
            booking_id=booking_id,
            page_token=cursor or "",
            reseller_id=reseller_id or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._orders.ListBookingDetails(request, timeout=self._timeout),
        )

    async def find_booking_cancellations_for_bookings(
        self,
        bookings: Sequence[models_pb2.Booking],
        reseller_id: str | None = None,
    ) -> list[tuple[models_pb2.Booking, models_pb2.BookingCancellation | None]]:
        bookings_and_cancellations = []
        for booking in bookings:
            try:
                booking_cancellation = (
                    await self.get_booking_cancellation_by_booking_id(
                        booking_id=booking.id,
                        reseller_id=reseller_id or "",
                    )
                )
            except errors.NotFoundError:
                booking_cancellation = None

            bookings_and_cancellations.append((booking, booking_cancellation))

        return bookings_and_cancellations

    async def handle_cancellation_ticket_completed(
        self,
        ticket_id: str,
        status: orders_pb2.Status.ValueType,
    ) -> None:
        request = orders_pb2.HandleCancellationTicketCompletedRequest(
            ticket_id=ticket_id,
            status=status,
        )

        await errors.handle_grpc_errors(
            self._orders.HandleCancellationTicketCompleted(
                request,
                timeout=self._timeout,
            ),
        )
