from types import MappingProxyType
from typing import Any

import httpx
import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status
from starlette.background import BackgroundTask

from snowfall.project.junction.extensions.service.mobile_api import (
    payments,
    plus_client,
    repository,
    smtp,
    validators,
)
from snowfall.project.junction.extensions.service.mobile_api.tasks import orders
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import models as stdlib_models
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction.go import client
from snowfall.vendor.junction.go import models as vendor_models

MIN_CHARGE = MappingProxyType(
    {
        "EUR": 50,
        "SEK": 500,
    },
)
_ID = "_id"


class MessageOrder(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
        smtp_client: smtp.EmailClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        mobile_order = await orders_repository.find_by_id(
            request.path_params["orderId"],
        )
        if not mobile_order or mobile_order.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        order_response = await junction_client.get_order_by_id(
            identifier=mobile_order.id,
            include=["journey", "bookings.details"],
        )
        await orders.email_booking_details(
            order_response,
            smtp_client,
            body["email"],
        )
        return responses.Response(status_code=status.HTTP_202_ACCEPTED)


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
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
            include=request.scope["parsed_query_string"].get(
                "include",
                [],
            ),
        )

        order_response["data"]["relationships"]["payment"] = {
            "data": {
                "id": mobile_order.payment_intent_id,
                "type": "payments",
            },
        }
        if mobile_order.voucher_code:
            order_response["data"]["relationships"]["voucher"] = {
                "data": {
                    "id": mobile_order.voucher_code,
                    "type": "vouchers",
                },
            }

        response_body = stdlib_models.Body(data=order_response["data"])

        if order_response.get("included"):
            response_body.included = order_response.get("included")
        return stdlib_models.JsonApiResponse(response_body)


class Orders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        # TODO: create pagination for this one (!581)
        user_mobile_orders = await orders_repository.get_user_orders(
            request.user.username,
        )
        user_orders: dict[str, list[Any]] = {"data": [], "included": []}
        async for mobile_order in user_mobile_orders:
            order_response = await junction_client.get_order_by_id(
                identifier=mobile_order.id,
                include=request.scope["parsed_query_string"].get(
                    "include",
                    [],
                ),
            )
            order_response["data"]["relationships"]["payment"] = {
                "data": {
                    "id": mobile_order.payment_intent_id,
                    "type": "payments",
                },
            }
            user_orders["data"].append(order_response["data"])
            if order_response.get("included"):
                user_orders["included"].extend(order_response["included"])

        response_body = stdlib_models.Body(data=user_orders["data"])
        if user_orders.get("included"):
            response_body.included = user_orders.get("included")
        return stdlib_models.JsonApiResponse(response_body)

    @validators.voucher_validator
    async def post(  # noqa: WPS211, WPS210, WPS217, C901
        self,
        request: requests.Request,
        voucher: models_pb2.Voucher | None,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
        plus_http_client: plus_client.PlusClient = lagom.injectable,
        smtp_client: smtp.EmailClient = lagom.injectable,
        vouchers_repository: repository.VouchersRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        payment = body["payment"]
        voucher_code = body.get("voucher", "")
        (correct_amount, correct_state) = await check_payment_amount_and_state(
            payment,
            body["quote"],
            voucher,
            junction_client,
        )
        if not correct_amount:
            stripe.PaymentIntent.cancel(payment)
            # TODO: split this into invalid amount & invalid currency. Create err func
            return stdlib_models.JsonApiResponse(
                stdlib_models.Body(
                    errors=[
                        stdlib_models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="invalid_amount_or_currency",
                            detail=(
                                "Payment's amount or currency doesn't match with order"
                            ),
                            source=stdlib_models.ErrorSourcePointer(
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
                            source=stdlib_models.ErrorSourcePointer(
                                pointer="/data/relationships/payment",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        contact_details = body["contactDetails"]
        try:
            junction_order = await junction_client.create_order(
                body["quote"],
                [
                    vendor_models.Passenger(**vendor_models.dict_factory_to_snake(pax))
                    for pax in body["passengers"]
                ],
                vendor_models.ContactDetails(
                    email=contact_details["email"],
                    address=vendor_models.Address(
                        **vendor_models.dict_factory_to_snake(
                            contact_details["address"],
                        ),
                    ),
                    phone_number=contact_details["phoneNumber"],
                ),
                body.get("residenceAddress"),
                include=["journey"],
            )
        except httpx.HTTPStatusError as error:
            await payments.cancel(payment)
            raise error
        mobile_order = models_pb2.MobileOrder(
            id=junction_order["data"]["id"],
            payment_intent_id=payment,
            user_id=request.user.username,
            mobile_number=contact_details["phoneNumber"],
        )
        try:
            spnr = junction_order["included"][0]["attributes"]["reference"]
        except (KeyError, IndexError):
            spnr = "XX"
        if voucher_code:
            await vouchers_repository.use_voucher(voucher_code, payment)
            mobile_order.voucher_code = voucher_code
        stripe.PaymentIntent.modify(
            payment,
            metadata={"order_id": mobile_order.id, "spnr": spnr},
            receipt_email=contact_details["email"],
        )
        mobile_order.spnr = spnr
        await orders_repository.insert(mobile_order)

        task = BackgroundTask(
            orders.poll_order_status,
            junction_client,
            mobile_order.id,
            mobile_order.payment_intent_id,
            smtp_client,
            vouchers_repository,
            plus_http_client,
        )
        junction_order["data"]["relationships"]["payment"] = {
            "data": {
                "id": mobile_order.payment_intent_id,
                "type": "payments",
            },
        }
        return stdlib_models.JsonApiResponse(
            stdlib_models.Body(data=junction_order["data"]),
            status.HTTP_201_CREATED,
            background=task,
        )


async def check_payment_amount_and_state(
    payment_intent_id: str,
    quote: str,
    voucher: models_pb2.Voucher | None,
    junction_client: client.Client,
) -> tuple[bool, bool]:
    pi = stripe.PaymentIntent.retrieve(payment_intent_id)

    quote_response = await junction_client.get_offer_quote_by_id(
        quote,
    )
    quote_currency = money.Currency(
        quote_response["data"]["attributes"]["price"]["currency"],
    )
    quote_money = money.from_string(
        quote_response["data"]["attributes"]["price"]["amount"],
        quote_currency,
    )
    quote_amount = quote_money.amount
    if voucher:
        quote_amount -= money.from_protobuf(voucher.price).amount
    return (
        pi["amount"] == max(quote_amount, MIN_CHARGE[pi["currency"].upper()]),
        pi["status"] == "requires_capture",
    )
