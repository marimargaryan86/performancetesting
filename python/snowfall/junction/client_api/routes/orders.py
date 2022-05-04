import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import orders
from snowfall.common.v1alpha import models_pb2, phone_number_pb2, postal_address_pb2
from snowfall.junction.client_api import (
    models,
    pagination_helpers,
    request_helpers,
    resources,
)
from snowfall.junction.orders.v1alpha import models_pb2 as order_models_pb2


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            order = await client.get(request.path_params["orderId"])
        except orders.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
        )

    async def patch(
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        order = await orders_client.add_offers(
            order_id=request.path_params["orderId"],
            offer_ids=[
                offer_id for offer in body["offers"] for offer_id in offer["offerIds"]
            ],
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status.HTTP_202_ACCEPTED,
        )


class Orders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find(limit=pagination.limit, cursor=pagination.cursor)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OrderResource.from_proto(order, request)
                    for order in response.orders
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListOrders"),
                    response.next_page_token,
                    pagination,
                ),
            ),
        )

    async def post(
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        order = await orders_client.create(
            offer_ids=[
                offer_id for offer in body["offers"] for offer_id in offer["offerIds"]
            ],
            passengers=[
                order_models_pb2.Passenger(
                    first_name="First",
                    last_name="Last",
                    title=order_models_pb2.Passenger.Title.TITLE_MR,
                    gender=order_models_pb2.Passenger.Gender.GENDER_MALE,
                    date_of_birth=models_pb2.Date(
                        year=1967,  # noqa: WPS432
                        month=3,
                        day=23,  # noqa: WPS432
                    ),
                ),
            ],
            contact_details=order_models_pb2.ContactDetails(
                email="example@example.com",
                address=postal_address_pb2.PostalAddress(
                    address_lines=[
                        "Austin, TX",
                    ],
                    region_code="CH",
                    revision=0,
                ),
                phone=phone_number_pb2.PhoneNumber(
                    e164_number="+15552220123",
                    extension="",
                ),
            ),
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
