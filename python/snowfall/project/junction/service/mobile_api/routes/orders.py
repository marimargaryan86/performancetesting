import asyncio
from typing import Any, Sequence, Tuple

import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, smtp
from snowfall.project.junction.service.mobile_api.tasks import orders
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import models as stdlib_models
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction import client
from snowfall.vendor.junction import models as vendor_models

_ID = "_id"


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        mobile_order = await orders_repository.find_by_id(
            request.path_params["orderId"],
        )
        if not mobile_order:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        if mobile_order.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        order_response = await junction_client.get_order_by_id(
            identifier=mobile_order.id,
            include=request.scope["query_string"].get(
                "include",
                [],
            ),
        )
        response_body = stdlib_models.Body(data=order_response["data"])
        if order_response.get("included"):
            response_body.included = order_response.get("included")
        return stdlib_models.JsonApiResponse(response_body)


class Orders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        # TODO: create pagination for this one (!581)
        user_mobile_orders = await orders_repository.get_user_orders(
            request.user.username,
        )
        user_orders: dict[str, list[Any]] = {"data": [], "included": []}
        async for mobile_order in user_mobile_orders:
            order_response = await junction_client.get_order_by_id(
                identifier=mobile_order.id,
                include=request.scope["query_string"].get(
                    "include",
                    [],
                ),
            )
            user_orders["data"].append(order_response["data"])
            if order_response.get("included"):
                user_orders["included"].extend(order_response["included"])

        response_body = stdlib_models.Body(data=user_orders["data"])
        if user_orders.get("included"):
            response_body.included = user_orders.get("included")
        return stdlib_models.JsonApiResponse(response_body)

    async def post(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
        smtp_client: smtp.EmailClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        (correct_amount, correct_state) = await check_payment_amount_and_state(
            body["payment"],
            body["options"],
            junction_client,
        )
        if not correct_amount:
            stripe.PaymentIntent.cancel(body["payment"])
            return stdlib_models.JsonApiResponse(
                stdlib_models.Body(
                    errors=[
                        stdlib_models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="invalid_amount",
                            detail="Payment's amount does not match with order",
                            source=stdlib_models.ErrorSource(
                                pointer="/data/relationships/payment",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not correct_state:
            return stdlib_models.JsonApiResponse(
                stdlib_models.Body(
                    errors=[
                        stdlib_models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="invalid_payment_state",
                            detail="Payment Intent is not confirmed",
                            source=stdlib_models.ErrorSource(
                                pointer="/data/relationships/payment",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        junction_order = await junction_client.create_order(
            body["offer"],
            body["options"],
            [
                vendor_models.Passenger(**vendor_models.dict_factory_to_snake(pax))
                for pax in body["passengers"]
            ],
            vendor_models.ContactDetails(
                email=body["contactDetails"]["email"],
                address=vendor_models.Address(
                    **vendor_models.dict_factory_to_snake(
                        body["contactDetails"]["address"],
                    ),
                ),
                phone_number=body["contactDetails"]["phoneNumber"],
            ),
        )
        mobile_order = models_pb2.MobileOrder(
            id=junction_order["data"][_ID],
            payment_intent_id=body["payment"],
            user_id=request.user.username,
        )
        stripe.PaymentIntent.modify(
            body["payment"],
            metadata={"order_id": mobile_order.id},
        )

        await orders_repository.insert(mobile_order)

        asyncio.create_task(
            orders.poll_order_status(
                junction_client,
                mobile_order.id,
                mobile_order.payment_intent_id,
                smtp_client,
            ),
        )

        return stdlib_models.JsonApiResponse(
            stdlib_models.Body(data=junction_order["data"]),
            status.HTTP_201_CREATED,
        )


async def check_payment_amount_and_state(
    payment_intent_id: str,
    offer_options: Sequence[str],
    junction_client: client.JunctionClient,
) -> Tuple[bool, bool]:
    # TODO: check for currency as well (!473)
    offer_amount = 0
    for offer_option in offer_options:
        offer_option_response = (
            await junction_client.get_offer_options_by_offer_option_id(
                offer_option,
            )
        )
        offer_amount += int(
            float(offer_option_response["attributes"]["price"]["amount"]) * 100,
        )
    pi = stripe.PaymentIntent.retrieve(payment_intent_id)
    return pi["amount"] == offer_amount, pi["status"] == "confirmed"
