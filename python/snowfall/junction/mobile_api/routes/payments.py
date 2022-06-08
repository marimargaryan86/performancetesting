import json
from datetime import datetime

import lagom
import stripe
from starlette import endpoints, requests, responses

from snowfall.junction.mobile_api import repository
from snowfall.stdlib.integration.starlette import models, request_helpers

_email_key = "email"
_id_key = "_id"
_user_key = "user_id"
_name_key = "name"
_stripe_customer_id_key = "stripe_customer_id"
_password_key = str("password")
_stripe_version = "2020-08-27"


class Payments(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
        stripe_users_repository: repository.StripeUsersRepository = lagom.injectable,
        payment_intent_repository: repository.PaymentIntentRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        user_id = request.user.username
        user = await users_repository.get({_id_key: user_id})
        stripe_user = await stripe_users_repository.get({"internal_user_id": user_id})
        if not stripe_user:
            api_response_user = stripe.Customer.create(
                email=user[_email_key],
                name=user[_name_key],
            )
            stripe_user = {
                "_id": api_response_user.stripe_id,
                _stripe_customer_id_key: api_response_user.stripe_id,
                "internal_user_id": user_id,
                "created": datetime.utcfromtimestamp(api_response_user.created),
            }
            await stripe_users_repository.insert(stripe_user)

        ephemeral_key = stripe.EphemeralKey.create(
            customer=stripe_user[_id_key],
            stripe_version=_stripe_version,
        )

        intent = stripe.PaymentIntent.create(
            amount=body["amount"],
            currency=body["currency"],
            capture_method="manual",
            customer=stripe_user[_stripe_customer_id_key],
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={"offerId": body["offerId"]},
        )
        intent_object = {
            _id_key: intent.stripe_id,
            "client_secret": intent.client_secret,
            "status": intent.status,
            "internal_user_id": user_id,
            _stripe_customer_id_key: stripe_user[_stripe_customer_id_key],
            "api_response_history": [json.loads(intent.last_response.body)],
            "created": datetime.utcfromtimestamp(intent.created),
        }
        await payment_intent_repository.insert(intent_object)

        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=intent.stripe_id,
                    type="paymentIntent",
                    attributes={
                        "clientSecret": intent.client_secret,
                        "ephemeralKey": ephemeral_key.secret,
                        "customerId": stripe_user[_stripe_customer_id_key],
                    },
                ),
            ),
        )
