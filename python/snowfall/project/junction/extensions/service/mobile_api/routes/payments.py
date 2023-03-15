import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    validators,
)
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import models, request_helpers

_email_key = "email"
_id_key = "_id"
_user_key = "user_id"
_name_key = "name"
_stripe_customer_id_key = "stripe_customer_id"
_password_key = str("password")
_stripe_version = "2020-08-27"
_MIN_CHARGE = 500


async def get_or_create_stripe_customer(
    stripe_users_repository: repository.StripeUsersRepository,
    users_repository: repository.UsersRepository,
    user_id: str,
) -> str:
    stripe_user = await stripe_users_repository.get(user_id)
    if not stripe_user:
        user = await users_repository.find_by_id(user_id)
        if user is None:
            raise exceptions.HTTPException(status.HTTP_502_BAD_GATEWAY)
        api_response_user = stripe.Customer.create(
            email=user.email,
            name=user.first_name,
        )
        stripe_user = models_pb2.StripeUser(
            id=api_response_user.stripe_id,
            internal_user_id=user_id,
        )
        await stripe_users_repository.insert(stripe_user)
    return stripe_user.id


class Payments(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
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
                request.user.username,
            )
            ephemeral_key_secret = stripe.EphemeralKey.create(
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
                    id=intent.stripe_id,
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
                amount=max(new_amount, _MIN_CHARGE),
            )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
