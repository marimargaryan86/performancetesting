import datetime
from typing import Any, Mapping, Sequence

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import orders as orders_adapter
from snowfall.project.junction.service.client_api import resources
from snowfall.project.junction.service.client_api.validators import (
    order_request_validator,
)
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.stdlib.format.protobuf import date_to_protobuf, slug_to_enum_value
from snowfall.stdlib.integration.starlette import (
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import phone_number_pb2, postal_address_pb2

_ADDRESS = "address"
_OFFER_AGGREGATE_ID = "offerAggregateId"


class Journey(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            journey = await client.get_journey(request.path_params["journeyId"])
        except orders_adapter.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.JourneyResource.from_proto(
                    journey=journey,
                    request=request,
                ),
            ),
        )


class Journeys(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_journeys(
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return models.JsonApiResponse(
            models.Body(
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
        )


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            order = await client.get_order(request.path_params["orderId"])
        except orders_adapter.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
        )


class Orders(endpoints.HTTPEndpoint):
    @order_request_validator
    async def post(
        self,
        request: requests.Request,
        orders_client: orders_adapter.Client,
        options: Sequence[order_models_pb2.TripOption],
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        journey = await orders_client.create_journey(
            contact_details=_create_contact_details(body["contactDetails"]),
        )
        order = await orders_client.place_order(
            journey_id=journey.id,
            passengers=_create_passengers(body["passengers"]),
            options=options,
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class OrdersByJourney(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        journey_id = request.path_params["journeyId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_orders_by_journey_id(
            journey_id=journey_id,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return models.JsonApiResponse(
            models.Body(
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
        )

    @order_request_validator
    async def post(
        self,
        request: requests.Request,
        orders_client: orders_adapter.Client,
        options: Sequence[order_models_pb2.TripOption],
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            order = await orders_client.place_order(
                journey_id=request.path_params["journeyId"],
                passengers=_create_passengers(body["passengers"]),
                options=options,
            )
        except orders_adapter.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        # todo: Expire (delete) the offer the order was placed for.

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class Booking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            booking = await client.get_booking(request.path_params["bookingId"])
        except orders_adapter.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.BookingResource.from_proto(
                    booking=booking,
                    request=request,
                ),
            ),
        )


class BookingsByOrder(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        order_id = request.path_params["orderId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_bookings_by_order_id(
            order_id=order_id,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.BookingResource.from_proto(booking, request)
                    for booking in response.bookings
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListBookingsByOrder", orderId=order_id),
                    response.next_page_token,
                    pagination,
                ),
            ),
        )


def _create_contact_details(
    contact_details: Mapping[str, Any],
) -> order_models_pb2.ContactDetails:
    address = contact_details[_ADDRESS]

    return order_models_pb2.ContactDetails(
        email=contact_details["email"],
        address=postal_address_pb2.PostalAddress(
            address_lines=address["addressLines"],
            region_code=address["countryCode"],
            postal_code=address["postalCode"],
            locality=address["city"],
            revision=0,
        ),
        phone=phone_number_pb2.PhoneNumber(
            e164_number=contact_details["phoneNumber"],
        ),
    )


def _create_passengers(
    passengers: Sequence[Mapping[str, Any]],
) -> list[order_models_pb2.Passenger]:
    return [
        order_models_pb2.Passenger(
            first_name=passenger["firstName"],
            last_name=passenger["lastName"],
            title=slug_to_enum_value(  # type: ignore[arg-type]
                descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
                name=passenger["title"],
            ),
            gender=slug_to_enum_value(  # type: ignore[arg-type]
                descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
                name=passenger["gender"],
            ),
            date_of_birth=date_to_protobuf(
                datetime.date.fromisoformat(passenger["dateOfBirth"]),
            ),
        )
        for passenger in passengers
    ]


class BookingDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            details = await client.get_booking_details(
                request.path_params["bookingDetailsId"],
            )
        except orders_adapter.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripBookingDetailsResource.from_proto(
                    details=details,
                    request=request,
                ),
            ),
        )


class BookingDetailsByBooking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        booking_id = request.path_params["bookingId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_booking_details_by_booking_id(
            booking_id=booking_id,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return models.JsonApiResponse(
            models.Body(
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
        )
