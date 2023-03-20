import datetime
from typing import Any, Mapping, Sequence

import lagom
import more_itertools
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import offers as offers_adapter
from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter import price_quotes as price_quotes_adapter
from snowfall.project.junction.service.client_api import resources, validators
from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.stdlib.format.protobuf import date_to_protobuf, slug_to_enum_value
from snowfall.stdlib.integration.starlette import (
    messages,
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
        journey = await client.get_journey(request.path_params["journeyId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.JourneyResource.from_proto(
                    journey=journey,
                    request=request,
                ),
            ),
            request=request,
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


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        order = await client.get_order(request.path_params["orderId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            request=request,
        )


class Orders(endpoints.HTTPEndpoint):
    @validators.order_request_validator
    async def post(  # noqa: WPS217
        self,
        request: requests.Request,
        price_quotes_client: price_quotes_adapter.Client = lagom.injectable,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        price_quote = await price_quotes_client.get(body["quote"])
        offer = await offers_client.get(price_quote.offer_id)

        journey = await orders_client.create_journey(
            contact_details=_create_contact_details(body["contactDetails"]),
        )
        order = await orders_client.place_order(
            journey_id=journey.id,
            passengers=_create_passengers(body["passengers"]),
            options=_create_trip_options(offer, price_quote),
            residence_address=_create_residence_address(
                body.get("residenceAddress", None),
            ),
            auth_token=request.scope.get("security", {"jwt": ""})["jwt"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status_code=status.HTTP_201_CREATED,
            request=request,
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

    async def post(
        self,
        request: requests.Request,
        price_quotes_client: price_quotes_adapter.Client = lagom.injectable,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        price_quote = await price_quotes_client.get(body["quote"])
        offer = await offers_client.get(price_quote.offer_id)

        order = await orders_client.place_order(
            journey_id=request.path_params["journeyId"],
            passengers=_create_passengers(body["passengers"]),
            options=_create_trip_options(offer, price_quote),
            residence_address=_create_residence_address(
                body.get("residenceAddress", None),
            ),
            auth_token=request.scope.get("security", {"jwt": ""})["jwt"],
        )
        # todo: Expire (delete) the offer the order was placed for.

        return await messages.create_response(
            body=models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status_code=status.HTTP_201_CREATED,
            request=request,
        )


class Booking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        booking = await client.get_booking(request.path_params["bookingId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.TripBookingResource.from_proto(
                    booking=booking,
                    request=request,
                ),
            ),
            request=request,
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

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.TripBookingResource.from_proto(booking, request)
                    for booking in response.bookings
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListBookingsByOrder", orderId=order_id),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
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


def _create_traveler_doc(
    passenger: Mapping[str, Any],
) -> order_models_pb2.DocumentDetails | None:
    document = passenger.get("travelerDocument")

    if not document:
        return None

    return order_models_pb2.DocumentDetails(
        document_type=slug_to_enum_value(
            enum=order_models_pb2.DocumentDetails.Type,
            name=document["documentType"],
        ),
        document_number=document["documentNumber"],
        issue_county=document["documentIssueCountry"],
        nationality=document["nationality"],
        exp_date=date_to_protobuf(
            datetime.date.fromisoformat(document["documentExpirationDate"]),
        ),
        residence_country_code=document.get("residenceCountryCode"),
    )


def _create_residence_address(
    residence_address: Mapping[str, Any],
) -> postal_address_pb2.PostalAddress | None:
    if not residence_address:
        return None

    return postal_address_pb2.PostalAddress(
        address_lines=residence_address["addressLines"],
        postal_code=residence_address["postalCode"],
        locality=residence_address["city"],
        region_code=residence_address["countryCode"],
    )


def _create_passengers(
    passengers: Sequence[Mapping[str, Any]],
) -> list[order_models_pb2.Passenger]:
    return [
        order_models_pb2.Passenger(
            first_name=passenger["firstName"],
            last_name=passenger["lastName"],
            title=slug_to_enum_value(
                enum=order_models_pb2.Passenger.Title,
                name=passenger["title"],
            ),
            gender=slug_to_enum_value(
                enum=order_models_pb2.Passenger.Gender,
                name=passenger["gender"],
            ),
            date_of_birth=date_to_protobuf(
                datetime.date.fromisoformat(passenger["dateOfBirth"]),
            ),
            doc_details=_create_traveler_doc(passenger),
        )
        for passenger in passengers
    ]


class BookingDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        details = await client.get_booking_details(
            request.path_params["bookingDetailsId"],
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


def _create_trip_options(
    offer: offer_models_pb2.OfferAggregate,
    price_quote: offer_models_pb2.PriceQuoteContainer,
) -> list[order_models_pb2.TripOption]:
    quote_mapping = {quote.option_id: quote for quote in price_quote.quotes}

    return [
        _create_trip_option(option, group, quote_mapping[option.id])
        for group in offer.groups
        for option in group.offers
        if option.id in price_quote.option_ids
    ]


def _create_trip_option(
    option: offer_models_pb2.Offer,
    group: offer_models_pb2.OfferGroup,
    price_quote: offer_models_pb2.PriceQuote,
) -> order_models_pb2.TripOption:
    return order_models_pb2.TripOption(
        id=option.id,
        price_quote_id=price_quote.id,
        details=[
            order_models_pb2.TripOptionDetails(
                segment=offer_segment,
                cabin_class=more_itertools.first(
                    [
                        detail.cabin_class
                        for detail in option.segment_details
                        if detail.offer_segment_id == offer_segment.id
                    ],
                ),
            )
            for offer_segment in group.segments
        ],
        price=price_quote.price,
    )
