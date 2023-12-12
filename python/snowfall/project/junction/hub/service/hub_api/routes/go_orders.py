from types import MappingProxyType

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import errors, orders
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.hub.service.hub_api import filters, resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.pay.adapter import refunds
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
    sorting,
)


class Booking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
        refunds_client: refunds.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("booking.view", request.user.permissions)

        booking = await client.get_booking(
            request.path_params["bookingId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        try:
            booking_cancellation = await client.get_booking_cancellation_by_booking_id(
                booking_id=booking.id,
                reseller_id=request.user.metadata.get("reseller_id", ""),
            )
        except errors.NotFoundError:
            booking_cancellation = None

        try:
            refund = (
                await refunds_client.get(
                    identifier=booking.transaction_id,
                    selector="transaction_id",
                )
                if booking.transaction_id
                else None
            )
        except errors.NotFoundError:
            refund = None

        return await messages.create_response(
            body=models.Body(
                data=resources.TripBookingResource.from_proto(
                    booking=booking,
                    booking_cancellation=booking_cancellation,
                    refund=refund,
                    request=request,
                ),
            ),
            request=request,
        )


class BookingsByOrder(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
        refunds_client: refunds.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("booking.view", request.user.permissions)

        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_bookings_by_order_id(
            order_id=request.path_params["orderId"],
            limit=pagination.limit,
            cursor=pagination.cursor,
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        booking_cancellations_response = (
            await client.find_booking_cancellations_by_booking_ids(
                booking_ids=[booking.id for booking in response.bookings],
                reseller_id=request.user.metadata.get("reseller_id", ""),
            )
        )

        refunds_response = await refunds_client.find(
            limit=len(response.bookings),
            transaction_ids=[
                booking.transaction_id
                for booking in response.bookings
                if booking.transaction_id
            ],
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.TripBookingResource.from_proto(
                        booking=booking,
                        booking_cancellation=next(
                            (
                                booking_cancellation
                                for booking_cancellation in booking_cancellations_response.booking_cancellations
                                if booking_cancellation.booking_id == booking.id
                            ),
                            None,
                        ),
                        refund=next(
                            (
                                refund
                                for refund in refunds_response.refunds
                                if refund.transaction_id == booking.transaction_id
                            ),
                            None,
                        ),
                        request=request,
                    )
                    for booking in response.bookings
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListBookingsByOrder",
                        orderId=request.path_params["orderId"],
                    ),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class DetailsByBooking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("booking.view", request.user.permissions)

        booking_id = request.path_params["bookingId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_booking_details_by_booking_id(
            booking_id=booking_id,
            reseller_id=request.user.metadata.get("reseller_id", ""),
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.TripBookingDetailsResource.from_proto(details, request)
                    for details in response.details
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListDetailsByBooking", bookingId=booking_id),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class BookingDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("booking.view", request.user.permissions)

        details = await client.get_booking_details(
            request.path_params["bookingDetailsId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripBookingDetailsResource.from_proto(
                    details=details,
                    request=request,
                ),
            ),
            request=request,
        )


class Journeys(endpoints.HTTPEndpoint):
    _sort = MappingProxyType({
        "id": "id",
        "reference": "passenger_name_record",
        "createdAt": "created_at",
    })

    _status_mapping = MappingProxyType({
        "unspecified": models_pb2.Booking.Status.STATUS_UNSPECIFIED,
        "pending": models_pb2.Booking.Status.STATUS_PENDING,
        "confirmed": models_pb2.Booking.Status.STATUS_CONFIRMED,
        "rejected": models_pb2.Booking.Status.STATUS_REJECTED,
        "notTicketed": models_pb2.Booking.Status.STATUS_NOT_TICKETED,
        "error": models_pb2.Booking.Status.STATUS_ERROR,
        "cancelled": models_pb2.Booking.Status.STATUS_CANCELLED,
    })

    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("journey.view", request.user.permissions)
        pagination = pagination_helpers.get_pagination(request)

        response = await client.find_journeys(
            limit=pagination.limit,
            cursor=pagination.cursor,
            sort_by=sorting.get_sort(request, self._sort),
            reseller_id=request.user.metadata.get("reseller_id", ""),
            filter_by=filters.get_journey_filters(request, self._status_mapping),
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.JourneyResource.from_proto(journey, request)
                    for journey in response.journeys
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListJourneys"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class Journey(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("journey.view", request.user.permissions)

        journey = await client.get_journey(
            request.path_params["journeyId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.JourneyResource.from_proto(
                    journey=journey,
                    request=request,
                ),
            ),
            request=request,
        )


class OrdersByJourney(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("order.view", request.user.permissions)

        journey_id = request.path_params["journeyId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_orders_by_journey_id(
            journey_id=journey_id,
            reseller_id=request.user.metadata.get("reseller_id", ""),
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.OrderResource.from_proto(order, request)
                    for order in response.orders
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListOrdersByJourney", journeyId=journey_id),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("order.view", request.user.permissions)

        order = await client.get_order(
            request.path_params["orderId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            request=request,
        )


class CancellationRequest(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("cancel.view", request.user.permissions)

        cancellation_request = await client.get_cancellation_request(
            identifier=request.path_params["cancellationRequestId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.CancellationRequestResource.from_proto(
                    cancellation_request=cancellation_request,
                    request=request,
                ),
            ),
            request=request,
        )

    async def post(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("cancel.add", request.user.permissions)

        body = await request_helpers.flatten_request(request)
        cancellation_request = await client.create_cancellation_request(
            booking_ids=body["bookings"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.CancellationRequestResource.from_proto(
                    cancellation_request=cancellation_request,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class BookingsCancellationByBooking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("cancel.view", request.user.permissions)

        cancellation = await client.get_booking_cancellation_by_booking_id(
            booking_id=request.path_params["bookingId"],
            reseller_id=request.user.metadata.get("reseller_id", ""),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BookingCancellationResource.from_proto(
                    booking_cancellation=cancellation,
                    request=request,
                ),
            ),
            request=request,
        )
