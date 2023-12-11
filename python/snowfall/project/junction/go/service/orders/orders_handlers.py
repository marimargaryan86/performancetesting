import asyncio
import dataclasses
from collections.abc import Awaitable, Iterable, Mapping, Sequence
from typing import NamedTuple

from grpc import StatusCode, aio

from snowfall.project.junction.go.service.gateway.v1 import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.project.junction.go.service.orders.orders import (
    BookingRepository,
    CancellationRequestsRepository,
    JourneyRepository,
)
from snowfall.project.junction.go.service.orders.v1 import (
    amqp_pb2,
    models_pb2,
    orders_pb2,
)
from snowfall.project.pay.adapter import refunds as refunds_adapter
from snowfall.project.pay.service.refunds.v1 import models_pb2 as refund_models_pb2
from snowfall.project.pay.service.refunds.v1 import models_pb2 as refunds_model_pb2
from snowfall.stdlib import money, sequence, string
from snowfall.stdlib.format.protobuf import protobuf_to_datetime
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import rich_status
from snowfall.vendor.zendesk.client import ZendeskClient
from snowfall.vendor.zendesk.models import (
    cancellation_request as cancellation_request_models,
)


async def _extract_bookings_and_orders(
    journeys: Sequence[models_pb2.Journey],
    booking_ids: Sequence[str],
) -> dict[str, tuple[models_pb2.Booking, models_pb2.Order, models_pb2.Journey]]:
    return {  # noqa: WPS224
        booking.id: (booking, order, journey)
        for journey in journeys
        for order in journey.orders
        for booking in order.bookings
        if booking.id in booking_ids
    }


async def _get_journeys(
    journey_repository: JourneyRepository,
    booking_ids: Sequence[str],
) -> Sequence[models_pb2.Journey]:
    journeys_result = await journey_repository.find_by_booking_ids(booking_ids)
    return [journey async for journey in journeys_result]


class CreateCancellationRequestHandler(object):
    def __init__(
        self,
        request: orders_pb2.CreateCancellationRequestRequest,
        context: aio.ServicerContext,
        journeys: JourneyRepository,
        cancellations: CancellationRequestsRepository,
        cancellation_task_producer: producer.Producer,
    ):
        self._request = request
        self._context = context
        self._journeys = journeys
        self._cancellations = cancellations
        self._cancellation_task_producer = cancellation_task_producer

    async def execute(
        self,
    ) -> orders_pb2.CreateCancellationRequestResponse:
        document = self._request.cancellation_request

        booking_ids = [
            cancellation.booking_id for cancellation in document.booking_cancellations
        ]
        journeys = await _get_journeys(self._journeys, booking_ids)
        bookings_and_orders = await _extract_bookings_and_orders(
            journeys,
            booking_ids,
        )
        bookings = [booking for booking, _, _ in bookings_and_orders.values()]

        await self._validate(booking_ids, journeys, bookings)

        document.id = string.uuid()
        document.status = models_pb2.CancellationRequest.STATUS_PENDING

        if not document.reseller_id:
            document.reseller_id = journeys[0].reseller_id

        document = await self._cancellations.insert(
            document,
        )

        await self._cancellation_task_producer.publish(
            msg=amqp_pb2.HandleCancellationTask(
                cancellation_request_id=document.id,
            ),
            routing_key="orders.cancellations",
        )

        return orders_pb2.CreateCancellationRequestResponse(
            cancellation_request=document,
        )

    async def _validate(
        self,
        booking_ids: Sequence[str],
        journeys: Sequence[models_pb2.Journey],
        bookings: Sequence[models_pb2.Booking],
    ) -> None:
        await self._validate_bookings_not_empty(booking_ids)
        await self._validate_bookings_belong_to_reseller(journeys)
        await self._validate_bookings_exist(bookings, booking_ids)
        await self._validate_bookings_statuses(bookings)
        await self._validate_not_duplication(booking_ids)

    async def _validate_bookings_not_empty(self, booking_ids: Sequence[str]) -> None:
        if not booking_ids:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="At least one booking ID should be provided",
                ),
            )

    async def _validate_bookings_belong_to_reseller(
        self,
        journeys: Sequence[models_pb2.Journey],
    ) -> None:
        reseller_id = self._request.cancellation_request.reseller_id
        if reseller_id:
            bookings_belong_to_reseller = all(
                reseller_id == journey.reseller_id for journey in journeys
            )
            if not bookings_belong_to_reseller:
                await rich_status.abort_with_rich_status(
                    context=self._context,
                    status=rich_status.build_precondition_failure(
                        subject="booking_ids",
                        description="Some of the bookings aren't found",
                    ),
                )

    async def _validate_bookings_exist(
        self,
        bookings: Sequence[models_pb2.Booking],
        booking_ids: Sequence[str],
    ) -> None:
        if len(bookings) != len(booking_ids):
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="Some of the bookings aren't found",
                ),
            )

    async def _validate_bookings_statuses(
        self,
        bookings: Sequence[models_pb2.Booking],
    ) -> None:
        allowed_statuses = [
            models_pb2.Booking.STATUS_CONFIRMED,
            models_pb2.Booking.STATUS_NOT_TICKETED,
        ]

        if not all(booking.status in allowed_statuses for booking in bookings):
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="One of the bookings is in inappropriate status",
                ),
            )

    async def _validate_not_duplication(self, booking_ids: Sequence[str]) -> None:
        cancellations = await self._cancellations.find_by_booking_ids(
            list(booking_ids),
        )
        if [cancellation async for cancellation in cancellations]:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description=(
                        "One or more bookings from the provided list are already"
                        " requested for cancellation"
                    ),
                ),
            )


def _update_overall_cancellation_status(
    cancellation: models_pb2.CancellationRequest,
) -> None:
    all_bookings_cancelled = all(
        booking_cancellation.status
        in {
            models_pb2.BookingCancellation.STATUS_REJECTED,
            models_pb2.BookingCancellation.STATUS_REFUND_DUE,
            models_pb2.BookingCancellation.STATUS_NO_REFUND,
            models_pb2.BookingCancellation.STATUS_REFUND_ISSUED,
        }
        for booking_cancellation in cancellation.booking_cancellations
    )

    if all_bookings_cancelled:
        cancellation.status = models_pb2.CancellationRequest.STATUS_COMPLETED


class CancellationTicketCompletedHandler(object):
    def __init__(
        self,
        request: orders_pb2.HandleCancellationTicketCompletedRequest,
        context: aio.ServicerContext,
        bookings: BookingRepository,
        cancellations: CancellationRequestsRepository,
        refund_client: refunds_adapter.Client,
    ):
        self._request = request
        self._context = context
        self._bookings = bookings
        self._cancellations = cancellations
        self._refund_client = refund_client

    async def execute(  # noqa: WPS217
        self,
    ) -> orders_pb2.HandleCancellationTicketCompletedResponse:
        cancellation_request = await self._cancellations.find_by_ticket_id(
            ticket_id=self._request.ticket_id,
        )

        if not cancellation_request:
            return await self._context.abort(StatusCode.NOT_FOUND)

        booking_cancellation = next(
            booking_cancellation
            for booking_cancellation in cancellation_request.booking_cancellations
            if booking_cancellation.ticket_id == self._request.ticket_id
        )
        ticket_status = self._request.status
        booking = await self._get_booking(booking_id=booking_cancellation.booking_id)

        match ticket_status:
            case orders_pb2.Status.STATUS_REJECTED:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_REJECTED
                )
            case orders_pb2.Status.STATUS_NO_REFUND:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_NO_REFUND
                )
                await self._update_booking_status(booking)
            case orders_pb2.Status.STATUS_REFUND_DUE:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_REFUND_DUE
                )
                await self._update_booking_status(booking)
                await self._refund_client.create(
                    refund=refunds_model_pb2.Refund(
                        transaction_id=booking.transaction_id,
                    ),
                )

        _update_overall_cancellation_status(cancellation_request)
        await self._cancellations.update(document=cancellation_request)

        return orders_pb2.HandleCancellationTicketCompletedResponse(
            booking_cancellation=booking_cancellation,
        )

    async def _get_booking(
        self,
        booking_id: str,
    ) -> models_pb2.Booking:
        booking = await self._bookings.find_by_id(document_id=booking_id)

        if booking is None:
            return await self._context.abort(StatusCode.NOT_FOUND)

        return booking

    async def _update_booking_status(self, booking: models_pb2.Booking) -> None:
        booking.status = models_pb2.Booking.STATUS_CANCELLED
        await self._bookings.update(booking)


def _create_order_model(
    order: models_pb2.Order,
) -> cancellation_request_models.Order:
    return cancellation_request_models.Order(
        order_id=order.id,
        passengers=[
            cancellation_request_models.Passengers(
                first_name=passenger.first_name,
                last_name=passenger.last_name,
            )
            for passenger in order.passengers
        ],
    )


def _create_booking_model(
    booking: models_pb2.Booking,
) -> cancellation_request_models.Booking:
    total_price = money.from_protobuf(booking.total_price)
    return cancellation_request_models.Booking(
        booking_id=booking.id,
        price=cancellation_request_models.Price(
            amount=str(total_price),
            currency=total_price.currency.code,
        ),
        provider_name=booking.provider_name,
        trip_reference=booking.trip_result.record_locator,
        operator_booking_references=[
            cancellation_request_models.OperatorBookingReference(
                operator_booking_reference=booking_ref,
            )
            for booking_ref in booking.trip_result.operator_booking_references
        ],
        trip_options=[
            cancellation_request_models.Segment(
                operator=trip_option.segment.operator,
                legs=[
                    cancellation_request_models.Leg(
                        origin_name=leg.origin.name,
                        destination_name=leg.destination.name,
                        departure_date=str(protobuf_to_datetime(leg.departure_at)),
                    )
                    for leg in trip_option.segment.legs
                ],
            )
            for trip_option in booking.trip_option.details
        ],
    )


def _create_journey_model(
    journey: models_pb2.Journey,
) -> cancellation_request_models.Journey:
    return cancellation_request_models.Journey(
        reseller_id=journey.reseller_id,
        passenger_name_record=journey.passenger_name_record,
    )


@dataclasses.dataclass(frozen=True)
class _ManualItem(object):
    booking_id: str
    refunded_us: money.Money | None = None


class _IdContainer(NamedTuple):
    composite_id: str
    booking_id: str


def _map_provider_references_to_ids(
    booking_cancellations: Sequence[models_pb2.BookingCancellation],
    bookings_map: dict[str, models_pb2.Booking],
) -> dict[str, _IdContainer]:
    mapped_data = {}

    for booking_cancellation in booking_cancellations:
        booking = bookings_map[booking_cancellation.booking_id]
        mapped_data[booking.trip_result.provider_booking_reference] = _IdContainer(
            composite_id=sequence.to_composite_id(
                [
                    booking.provider_id,
                    booking.trip_result.provider_booking_reference,
                ],
            ),
            booking_id=booking_cancellation.booking_id,
        )

    return mapped_data


@dataclasses.dataclass(frozen=True)
class _BookingsInfo(object):
    id_to_booking: Mapping[str, models_pb2.Booking]
    provider_reference_to_ids: Mapping[str, _IdContainer]


class _ProviderCancellationFailedError(Exception):
    """Raised when provider cancellation didn't succeed."""


class CreateCancellationTaskHandler(object):
    def __init__(
        self,
        gateway: bookings_pb2_grpc.BookingServiceStub,
        refund_client: refunds_adapter.GrpcClient,
        journeys: JourneyRepository,
        bookings: BookingRepository,
        cancellations: CancellationRequestsRepository,
        zendesk_client: ZendeskClient,
        cancellation_group_id: int,
    ):
        self._gateway = gateway
        self._refund_client = refund_client
        self._journeys = journeys
        self._bookings = bookings
        self._cancellations = cancellations
        self._zendesk_client = zendesk_client
        self._cancellation_group_id = cancellation_group_id
        self._logger = stdout.get_logger()

    async def execute(self, cancellation_request_id: str) -> None:
        cancellation_request = await self._cancellations.find_by_id(
            document_id=cancellation_request_id,
        )

        if not cancellation_request:
            self._logger.error(
                "Cancellation request not found",
                cancellation_request_id=cancellation_request_id,
            )

            return

        bookings_data = await self._get_bookings_data(cancellation_request)

        new_cancellations, manual_items = await self._handle_automatic_cancellation(
            bookings_data=bookings_data,
        )

        new_cancellations.extend(
            await self._handle_manual_flow(manual_items),
        )

        await self._update_statuses(
            cancellation_request=cancellation_request,
            cancellations=new_cancellations,
            provider_reference_to_ids=bookings_data.provider_reference_to_ids,
        )

    async def _handle_automatic_cancellation(  # noqa: WPS231
        self,
        bookings_data: _BookingsInfo,
    ) -> tuple[list[models_pb2.BookingCancellation], list[_ManualItem]]:
        coros = tuple(
            self._gateway.CancelBooking(
                bookings_pb2.CancelBookingRequest(
                    booking_id=id_container.composite_id,
                ),
            )
            for id_container in bookings_data.provider_reference_to_ids.values()
        )

        new_cancellations = []
        manual_items = []
        initial_booking_ids = set(bookings_data.id_to_booking.keys())

        for coro in asyncio.as_completed(coros):
            try:
                cancellation_response = await self._cancel(coro)
            except _ProviderCancellationFailedError:
                continue
            else:
                booking_id = bookings_data.provider_reference_to_ids[
                    cancellation_response.cancellation.booking_id
                ].booking_id
                initial_booking_ids.remove(booking_id)

            try:
                await self._create_pay_refund(
                    cancellation_response=cancellation_response,
                    booking=bookings_data.id_to_booking[booking_id],
                )
            except aio.AioRpcError:
                self._logger.exception("Failed to create refund in pay")

                manual_items.append(
                    _ManualItem(
                        booking_id=booking_id,
                        refunded_us=money.from_protobuf(
                            cancellation_response.cancellation.refunded_us,
                        ),
                    ),
                )

                continue

            new_cancellations.append(cancellation_response.cancellation)

        manual_items.extend(
            _ManualItem(booking_id=booking_id) for booking_id in initial_booking_ids
        )

        return new_cancellations, manual_items

    async def _cancel(
        self,
        coro: Awaitable[bookings_pb2.CancelBookingResponse],
    ) -> bookings_pb2.CancelBookingResponse:
        try:
            cancellation_response = await coro
        except aio.AioRpcError as err:
            if err.code() != StatusCode.UNIMPLEMENTED:
                self._logger.exception("Cancellation failed")

            raise _ProviderCancellationFailedError from err

        failed_by_status = (
            cancellation_response.cancellation.status
            == models_pb2.BookingCancellation.STATUS_REFUND_FAILED
        )

        if failed_by_status:
            raise _ProviderCancellationFailedError

        return cancellation_response

    async def _handle_manual_flow(
        self,
        manual_items: Sequence[_ManualItem],
    ) -> list[models_pb2.BookingCancellation]:
        booking_ids = [manual_item.booking_id for manual_item in manual_items]
        journeys = await _get_journeys(
            journey_repository=self._journeys,
            booking_ids=booking_ids,
        )
        bookings_and_orders = await _extract_bookings_and_orders(
            journeys=journeys,
            booking_ids=booking_ids,
        )
        coros = []

        for manual_item in manual_items:
            booking, order, journey = bookings_and_orders[manual_item.booking_id]

            coros.append(
                self._zendesk_client.create_support_ticket(
                    payload=self._zendesk_client.create_cancel_request_payload(
                        booking=_create_booking_model(booking),
                        order=_create_order_model(order),
                        journey=_create_journey_model(journey),
                        group_id=self._cancellation_group_id,
                        refunded_us=manual_item.refunded_us,
                    ),
                ),
            )
        ticket_ids = await asyncio.gather(*coros, return_exceptions=True)
        cancellations = []

        for idx, ticket_id in enumerate(ticket_ids):
            if isinstance(ticket_id, Exception):
                self._logger.exception(
                    "Failed to create a Zendesk ticket",
                    manual_item=manual_items[idx],
                    exc_info=(
                        type(ticket_id),
                        ticket_id,
                        ticket_id.__traceback__,
                    ),
                )

                continue

            cancellations.append(
                models_pb2.BookingCancellation(
                    booking_id=manual_items[idx].booking_id,
                    ticket_id=str(ticket_id),
                    status=models_pb2.BookingCancellation.STATUS_PENDING,
                ),
            )

        return cancellations

    async def _booking_id_to_booking(
        self,
        booking_ids: Iterable[str],
    ) -> dict[str, models_pb2.Booking]:
        booking_ids_copy = tuple(booking_ids)

        bookings_iterator = await self._bookings.find(
            ids=booking_ids_copy,
            cursor="",
        )
        booking_id_to_booking = {}

        async for booking in bookings_iterator:
            booking_id_to_booking[booking.id] = booking

        if len(booking_id_to_booking) != len(booking_ids_copy):
            self._logger.error(
                "Some bookings were not found",
                booking_ids=booking_ids,
                found_booking_ids=list(booking_id_to_booking.keys()),
            )

        return booking_id_to_booking

    async def _update_statuses(
        self,
        cancellation_request: models_pb2.CancellationRequest,
        cancellations: Sequence[models_pb2.BookingCancellation],
        provider_reference_to_ids: Mapping[str, _IdContainer],
    ) -> None:
        for initial_booking_cancellation in cancellation_request.booking_cancellations:
            try:
                new_booking_cancellation = next(
                    cancel_obj
                    for cancel_obj in cancellations
                    if provider_reference_to_ids[cancel_obj.booking_id].booking_id
                    == initial_booking_cancellation.booking_id
                )
            except StopIteration:
                self._logger.exception(
                    "Failed to find an updated cancellation",
                    initial_booking_cancellation=initial_booking_cancellation,
                )

                continue

            initial_booking_cancellation.status = new_booking_cancellation.status

        _update_overall_cancellation_status(cancellation_request)
        await self._cancellations.update(document=cancellation_request)

    async def _create_pay_refund(
        self,
        cancellation_response: bookings_pb2.CancelBookingResponse,
        booking: models_pb2.Booking,
    ) -> None:
        refunded_us_money = money.from_protobuf(
            proto=cancellation_response.cancellation.refunded_us,
        )

        if refunded_us_money.amount:
            await self._refund_client.create(
                refund_models_pb2.Refund(
                    refunded_us=refunded_us_money.protobuf(),
                    transaction_id=booking.transaction_id,
                ),
            )

    async def _get_bookings_data(
        self,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> _BookingsInfo:
        id_to_booking = await self._booking_id_to_booking(
            booking_ids=[
                booking_cancellation.booking_id
                for booking_cancellation in cancellation_request.booking_cancellations
            ],
        )

        return _BookingsInfo(
            id_to_booking=id_to_booking,
            provider_reference_to_ids=_map_provider_references_to_ids(
                booking_cancellations=cancellation_request.booking_cancellations,
                bookings_map=id_to_booking,
            ),
        )
