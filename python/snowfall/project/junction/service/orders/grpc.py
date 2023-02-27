from grpc import StatusCode, aio

from snowfall.project.junction.service.orders.amqp import OrderProducer
from snowfall.project.junction.service.orders.orders import (
    BookingDetailsRepository,
    BookingRepository,
    JourneyRepository,
    OrderRepository,
)
from snowfall.project.junction.service.orders.v1alpha import orders_pb2, orders_pb2_grpc
from snowfall.stdlib.transport.grpc import metadata, service


class OrderService(
    service.Service,
    orders_pb2_grpc.OrderServiceServicer,
):
    def __init__(
        self,
        journeys: JourneyRepository,
        orders: OrderRepository,
        bookings: BookingRepository,
        booking_details: BookingDetailsRepository,
        publisher: OrderProducer,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._journeys = journeys
        self._orders = orders
        self._bookings = bookings
        self._booking_details = booking_details
        self._publisher = publisher

    def get_name(self) -> str:
        return orders_pb2.DESCRIPTOR.services_by_name["OrderService"].full_name

    def register(self, server: aio.Server) -> None:
        orders_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def CreateJourney(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.CreateJourneyRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.CreateJourneyResponse:
        return orders_pb2.CreateJourneyResponse(
            journey=await self._journeys.create(
                contact_details=request.contact_details,
            ),
        )

    async def GetJourney(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetJourneyRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetJourneyResponse:
        journey = await self._journeys.find_by_id(request.id)

        if journey is None:
            await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetJourneyResponse(journey=journey)

    async def ListJourneys(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListJourneysRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListJourneysResponse:
        journeys_result = await self._journeys.find(
            ids=list(request.ids),
            cursor=request.page_token,
        )

        journeys_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListJourneysResponse(
            journeys=[journey async for journey in journeys_result],
            next_page_token=await journeys_result.cursor(),
        )

    async def PlaceOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.PlaceOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.PlaceOrderResponse:
        await metadata.get_auth_token(context)

        journey = await self._journeys.find_by_id(request.journey_id)

        if journey is None:
            await context.abort(StatusCode.NOT_FOUND)

        order = await self._orders.create_from_options(
            journey_id=request.journey_id,
            passengers=request.passengers,
            options=[option.trip_option for option in request.options],
            residence_address=request.residence_address,
        )

        await self._publisher.publish(
            journey=journey,  # type: ignore[arg-type]
            order=order,
        )

        return orders_pb2.PlaceOrderResponse(order=order)

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetOrderResponse:
        order = await self._orders.find_by_id(request.id)

        if order is None:
            await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetOrderResponse(order=order)

    async def ListOrders(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListOrdersRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListOrdersResponse:
        if request.journey_id:
            orders_result = await self._orders.find_by_journey_id(
                journey_id=request.journey_id,
                cursor=request.page_token,
            )
        else:
            orders_result = await self._orders.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
            )

        orders_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListOrdersResponse(
            orders=[order async for order in orders_result],
            next_page_token=await orders_result.cursor(),
        )

    async def GetBooking(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetBookingRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetBookingResponse:
        booking = await self._bookings.find_by_id(request.id)

        if booking is None:
            await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetBookingResponse(booking=booking)

    async def ListBookings(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListBookingsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListBookingsResponse:
        if request.order_id:
            bookings_result = await self._bookings.find_by_order_id(
                order_id=request.order_id,
                cursor=request.page_token,
            )
        else:
            bookings_result = await self._bookings.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
            )

        bookings_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListBookingsResponse(
            bookings=[order async for order in bookings_result],
            next_page_token=await bookings_result.cursor(),
        )

    async def GetBookingDetails(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetBookingDetailsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetBookingDetailsResponse:
        details = await self._booking_details.find_by_id(request.id)

        if details is None:
            await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetBookingDetailsResponse(details=details)

    async def ListBookingDetails(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListBookingDetailsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListBookingDetailsResponse:
        if request.booking_id:
            details_result = await self._booking_details.find_by_booking_id(
                booking_id=request.booking_id,
                cursor=request.page_token,
            )
        else:
            details_result = await self._booking_details.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
            )

        details_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListBookingDetailsResponse(
            details=[detail async for detail in details_result],
            next_page_token=await details_result.cursor(),
        )
