from types import MappingProxyType

import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    sorting,
)


class Booking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        booking = await client.get_booking(
            request.path_params["bookingId"],
            reseller_id=request.user.username,
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripBookingResource.from_proto(
                    booking=booking,
                    request=request,
                ),
            ),
            request=request,
        )


class Journeys(endpoints.HTTPEndpoint):
    _sort = MappingProxyType(
        {
            "id": "id",
            "reference": "passenger_name_record",
        },
    )

    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_journeys(
            limit=pagination.limit,
            cursor=pagination.cursor,
            sort_by=sorting.get_sort(request, self._sort),
            reseller_id=request.user.username,
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
        journey = await client.get_journey(
            request.path_params["journeyId"],
            reseller_id=request.user.username,
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
        journey_id = request.path_params["journeyId"]
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find_orders_by_journey_id(
            journey_id=journey_id,
            reseller_id=request.user.username,
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
        order = await client.get_order(
            request.path_params["orderId"],
            reseller_id=request.user.username,
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
