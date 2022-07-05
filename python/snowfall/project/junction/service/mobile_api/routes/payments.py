import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
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
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        user_id = request.user.username
        stripe_user = await stripe_users_repository.get(user_id)
        if not stripe_user:
            user = await users_repository.find_by_id(user_id)
            if user is None:
                raise exceptions.HTTPException(status.HTTP_502_BAD_GATEWAY)
            api_response_user = stripe.Customer.create(
                email=user.email,
                name=user.name,
            )
            stripe_user = models_pb2.StripeUser(
                id=api_response_user.stripe_id,
                internal_user_id=user_id,
            )
            await stripe_users_repository.insert(stripe_user)

        ephemeral_key = stripe.EphemeralKey.create(
            customer=stripe_user.id,
            stripe_version=_stripe_version,
        )
        intent = stripe.PaymentIntent.create(
            amount=body["amount"],
            currency=body["currency"],
            capture_method="manual",
            customer=stripe_user.id,
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={"offerId": body["offerId"]},
        )

        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=intent.stripe_id,
                    type="payments",
                    attributes={
                        "clientSecret": intent.client_secret,
                        "ephemeralKey": ephemeral_key.secret,
                        "customerId": stripe_user.id,
                    },
                ),
            ),
        )
