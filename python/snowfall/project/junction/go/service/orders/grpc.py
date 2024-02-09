from types import MappingProxyType

import more_itertools
from google.protobuf import json_format
from grpc import StatusCode, aio

from snowfall.project.junction.go.service.gateway.v1 import meta_pb2, meta_pb2_grpc
from snowfall.project.junction.go.service.orders import bookings, smtp
from snowfall.project.junction.go.service.orders.amqp import OrderProducer
from snowfall.project.junction.go.service.orders.orders import (
    BookingCancellationsRepository,
    BookingDetailsRepository,
    BookingRepository,
    CancellationRequestsRepository,
    JourneyRepository,
    OrderRepository,
)
from snowfall.project.junction.go.service.orders.orders_handlers import (
    CancellationTicketCompletedHandler,
    CreateCancellationRequestHandler,
)
from snowfall.project.junction.go.service.orders.v1 import orders_pb2, orders_pb2_grpc
from snowfall.project.pay.adapter import refunds as refunds_adapter
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import rich_status, service, sorting


class OrderService(
    service.Service,
    orders_pb2_grpc.OrderServiceServicer,
):
    _journey_sort = MappingProxyType(
        {
            "id": "_id",
            "passenger_name_record": "passenger_name_record",
            "created_at": "created_at",
        },
    )

    def __init__(
        self,
        journeys: JourneyRepository,
        orders: OrderRepository,
        booking_handler: bookings.BookingHandler,
        booking_repository: BookingRepository,
        booking_details: BookingDetailsRepository,
        booking_cancellations: BookingCancellationsRepository,
        cancellation_requests: CancellationRequestsRepository,
        publisher: OrderProducer,
        cancellation_task_producer: producer.Producer,
        smtp_client: smtp.EmailClient,
        default_page_size: int,
        environment: str,
        refund_client: refunds_adapter.Client,
        gateway_meta: meta_pb2_grpc.MetaServiceStub,
    ):
        self._default_page_size = default_page_size
        self._journeys = journeys
        self._orders = orders
        self._booking_handler = booking_handler
        self._bookings = booking_repository
        self._booking_details = booking_details
        self._booking_cancellations = booking_cancellations
        self._cancellation_requests = cancellation_requests
        self._publisher = publisher
        self._cancellation_task_producer = cancellation_task_producer
        self._refund_client = refund_client
        self._environment = environment
        self._smtp_client = smtp_client
        self._gateway_meta = gateway_meta
        self._logger = stdout.get_logger()

    def get_name(self) -> str:
        return orders_pb2.DESCRIPTOR.services_by_name["OrderService"].full_name

    def register(self, server: aio.Server) -> None:
        orders_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def CreateJourney(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.CreateJourneyRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.CreateJourneyResponse:
        if not request.reseller_id:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="reseller_id",
                    field_description="Field must not be empty",
                    description="Creating a journey requires a reseller ID",
                ),
            )

        return orders_pb2.CreateJourneyResponse(
            journey=await self._journeys.create(
                contact_details=request.contact_details,
                reseller_id=request.reseller_id,
            ),
        )

    async def GetJourney(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetJourneyRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetJourneyResponse:
        journey = await self._journeys.find_by_id(
            request.id,
            reseller_id=request.reseller_id,
        )

        if journey is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetJourneyResponse(journey=journey)

    async def ListJourneys(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListJourneysRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListJourneysResponse:
        journeys_result = await self._journeys.find(
            ids=list(request.ids),
            cursor=request.page_token,
            sort=sorting.get_sort(request.sort_by, self._journey_sort),
            reseller_id=request.reseller_id,
            filter_by=request.filter_by,
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
        journey = await self._journeys.find_by_id(request.journey_id)

        if journey is None:
            return await context.abort(StatusCode.NOT_FOUND)

        order = await self._orders.create_from_options(
            journey_id=request.journey_id,
            passengers=request.passengers,
            options=[option.trip_option for option in request.options],
            residence_address=request.residence_address,
        )

        await self._publisher.publish(
            journey=journey,
            order=order,
            reseller_id=journey.reseller_id,
        )

        return orders_pb2.PlaceOrderResponse(order=order)

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetOrderResponse:
        order = await self._orders.find_by_id(
            request.id,
            reseller_id=request.reseller_id,
        )

        if order is None:
            return await context.abort(StatusCode.NOT_FOUND)

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
                reseller_id=request.reseller_id,
            )
        else:
            orders_result = await self._orders.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
                reseller_id=request.reseller_id,
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
        booking = await self._bookings.find_by_id(request.id, request.reseller_id)

        if booking is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetBookingResponse(
            booking=more_itertools.first(
                await self._booking_handler.get_latest([booking]),
            ),
        )

    async def ListBookings(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListBookingsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListBookingsResponse:
        if request.order_id:
            bookings_result = await self._bookings.find_by_order_id(
                order_id=request.order_id,
                cursor=request.page_token,
                reseller_id=request.reseller_id,
            )
        elif request.transaction_ids.ids:
            bookings_result = await self._bookings.find(
                transaction_ids=list(request.transaction_ids.ids),
                cursor=request.page_token,
                reseller_id=request.reseller_id,
            )
        else:
            bookings_result = await self._bookings.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
                reseller_id=request.reseller_id,
            )

        bookings_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListBookingsResponse(
            bookings=await self._booking_handler.get_latest(
                [order async for order in bookings_result],
            ),
            next_page_token=await bookings_result.cursor(),
        )

    async def GetBookingDetails(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetBookingDetailsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetBookingDetailsResponse:
        details = await self._booking_details.find_by_id(
            request.id,
            reseller_id=request.reseller_id,
        )

        if details is None:
            return await context.abort(StatusCode.NOT_FOUND)

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
                reseller_id=request.reseller_id,
            )
        else:
            details_result = await self._booking_details.find(
                ids=list(request.ids.ids),
                cursor=request.page_token,
                reseller_id=request.reseller_id,
            )

        details_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListBookingDetailsResponse(
            details=[detail async for detail in details_result],
            next_page_token=await details_result.cursor(),
        )

    async def CreateCancellationRequest(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.CreateCancellationRequestRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.CreateCancellationRequestResponse:
        create_cancellation_handler = CreateCancellationRequestHandler(
            request,
            context,
            self._journeys,
            self._cancellation_requests,
            self._cancellation_task_producer,
        )
        return await create_cancellation_handler.execute()

    async def GetCancellationRequest(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetCancellationRequestRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetCancellationRequestResponse:
        cancellation = await self._cancellation_requests.find_by_id(
            document_id=request.id,
            reseller_id=request.reseller_id,
        )

        if cancellation is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetCancellationRequestResponse(
            cancellation_request=cancellation,
        )

    async def GetBookingCancellation(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetBookingCancellationRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetBookingCancellationResponse:
        booking_cancellation = await self._booking_cancellations.find_by_booking_id(
            document_id=request.booking_id,
            reseller_id=request.reseller_id,
        )

        if booking_cancellation is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetBookingCancellationResponse(
            booking_cancellation=booking_cancellation,
        )

    async def ListBookingCancellations(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListBookingCancellationsRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListBookingCancellationsResponse:
        if request.HasField("booking_ids"):
            booking_cancellations_result = (
                await self._booking_cancellations.find_by_booking_ids(
                    booking_ids=list(request.booking_ids.ids),
                    reseller_id=request.reseller_id,
                )
            )
        else:
            booking_cancellations_result = await self._booking_cancellations.find(
                ids=list(request.ids.ids),
                reseller_id=request.reseller_id,
            )

        return orders_pb2.ListBookingCancellationsResponse(
            booking_cancellations=[
                booking_cancellation
                async for booking_cancellation in booking_cancellations_result
            ],
        )

    async def HandleCancellationTicketCompleted(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.HandleCancellationTicketCompletedRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.HandleCancellationTicketCompletedResponse:
        ticket_completed_handler = CancellationTicketCompletedHandler(
            request,
            context,
            self._bookings,
            self._orders,
            self._journeys,
            self._cancellation_requests,
            self._smtp_client,
            self._refund_client,
            self._environment,
        )

        return await ticket_completed_handler.execute()

    async def UpdateBookingCancellation(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.UpdateBookingCancellationRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.UpdateBookingCancellationResponse:
        self._logger.info(
            "Got booking cancellation update request",
            request=json_format.MessageToJson(request),
        )

        booking_cancellation = await self._booking_cancellations.find_by_id(
            request.booking_cancellation.id,
        )

        if booking_cancellation is None:
            return await context.abort(StatusCode.NOT_FOUND)

        booking_cancellation = protobuf.apply_field_mask(
            request.update_mask,
            request.booking_cancellation,
            booking_cancellation,
        )

        booking_cancellation = await self._booking_cancellations.update(
            booking_cancellation,
        )

        return orders_pb2.UpdateBookingCancellationResponse(
            booking_cancellation=booking_cancellation,
        )

    async def Sleep(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.SleepRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.SleepResponse:
        response = await self._gateway_meta.Sleep(
            request=meta_pb2.SleepRequest(
                duration_seconds=request.duration_seconds,
            ),
        )

        return orders_pb2.SleepResponse(
            text=response.text,
        )
