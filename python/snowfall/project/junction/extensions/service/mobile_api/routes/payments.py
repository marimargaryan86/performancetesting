import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    validators,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import orders
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import models, request_helpers

_stripe_version = "2020-08-27"


async def get_or_create_stripe_customer(
    stripe_users_repository: repository.StripeUsersRepository,
    users_repository: repository.UsersRepository,
    guests_repository: repository.GuestsRepository,
    user_id: str,
) -> str:
    stripe_user = await stripe_users_repository.get(user_id)
    if stripe_user:
        return stripe_user.id

    user = await users_repository.find_by_id(user_id)
    if user:
        api_response_user = stripe.Customer.create(
            email=user.email,
            name=user.first_name,
        )
    else:
        guest = await guests_repository.find_by_id(user_id)
        if not guest:
            raise exceptions.HTTPException(status.HTTP_502_BAD_GATEWAY)
        api_response_user = stripe.Customer.create()
    stripe_user = models_pb2.StripeUser(
        id=api_response_user.stripe_id or "",
        internal_user_id=user_id,
    )
    await stripe_users_repository.insert(stripe_user)
    return stripe_user.id


class Payments(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
        guests_repository: repository.GuestsRepository = lagom.injectable,
        stripe_users_repository: repository.StripeUsersRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        intent_money = money.from_string(
            body["amount"],
            money.Currency(body["currency"]),
        )
        stripe_user_id = None
        ephemeral_key_secret = None
        if stripe_users_repository.create_stripe_customers:
            stripe_user_id = await get_or_create_stripe_customer(
                stripe_users_repository,
                users_repository,
                guests_repository,
                request.user.username,
            )
            ephemeral_key_secret = stripe.EphemeralKey.create(  # type: ignore[no-untyped-call]
                customer=stripe_user_id,
                stripe_version=_stripe_version,
            ).secret

        intent = stripe.PaymentIntent.create(
            amount=intent_money.amount,
            currency=intent_money.currency.code,
            capture_method="manual",
            customer=stripe_user_id,
            automatic_payment_methods={
                "enabled": True,
            },
        )

        attributes = {
            "clientSecret": intent.client_secret,
            "ephemeralKey": ephemeral_key_secret,
            "customerId": stripe_user_id,
        }
        attributes = {
            key: attr_value
            for key, attr_value in attributes.items()
            if attr_value is not None
        }

        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=intent.stripe_id or "",
                    type="payments",
                    attributes=attributes,
                ),
            ),
        )


class Payment(endpoints.HTTPEndpoint):
    @validators.voucher_validator
    async def patch(
        self,
        request: requests.Request,
        voucher: models_pb2.Voucher | None,
        vouchers_repository: repository.VouchersRepository = lagom.injectable,
    ) -> responses.Response:
        if voucher:
            payment_intent = stripe.PaymentIntent.retrieve(
                request.path_params["paymentIntentId"],
            )
            new_amount = (
                payment_intent["amount"] - money.from_protobuf(voucher.price).amount
            )

            stripe.PaymentIntent.modify(
                request.path_params["paymentIntentId"],
                amount=max(
                    new_amount,
                    orders.MIN_CHARGE[payment_intent["currency"].upper()],
                ),
            )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
