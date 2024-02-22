import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    validators,
)
from snowfall.project.junction.extensions.service.mobile_api.bootstrap import Switcher
from snowfall.project.junction.extensions.service.mobile_api.routes import orders
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.project.pay.adapter import credit_card_payment
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import (
    authentication,
    models,
    request_helpers,
)


async def get_or_create_stripe_customer(
    credit_card_client: credit_card_payment.Client,
    users_repository: repository.UsersRepository,
    guests_repository: repository.GuestsRepository,
    user_id: str,
    reseller_id: str,
) -> tuple[str, str]:
    stripe_user, ephemeral_key = await credit_card_client.get_credit_card_holder(
        user_id,
        reseller_id,
    )
    if stripe_user.id:
        return stripe_user.id, ephemeral_key

    user = await users_repository.find_by_id(user_id)
    if user:
        (
            api_response_user,
            ephemeral_key,
        ) = await credit_card_client.create_credit_card_holder(
            user_id,
            user.email,
            user.first_name,
            reseller_id,
        )
    else:
        guest = await guests_repository.find_by_id(user_id)
        if not guest:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        (
            api_response_user,
            ephemeral_key,
        ) = await credit_card_client.create_credit_card_holder(
            user_id,
            "",
            "",
            reseller_id,
        )
    return api_response_user.id, ephemeral_key


class Payments(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
        guests_repository: repository.GuestsRepository = lagom.injectable,
        credit_card_client: credit_card_payment.Client = lagom.injectable,
        switcher: Switcher = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        intent_money = money.from_string(
            body["amount"],
            money.Currency(body["currency"]),
        )
        stripe_user_id = None
        ephemeral_key_secret = None

        reseller_id, username = "", request.user.username
        if isinstance(request.user, authentication.AuthenticatedUser):
            reseller_id = request.user.metadata.get("reseller_id", "")
            username = request.user.identity

        if switcher.create_stripe_customers:
            stripe_user_id, ephemeral_key_secret = await get_or_create_stripe_customer(
                credit_card_client,
                users_repository,
                guests_repository,
                username,
                reseller_id,
            )

        payment_intent = await credit_card_client.create_credit_card_payment(
            amount=intent_money,
            credit_card_holder_id=stripe_user_id or "",
            enable_automatic_payment_method=True,
            reseller_id=reseller_id,
        )

        attributes = {
            "clientSecret": payment_intent.secret,
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
                    id=payment_intent.id,
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
        credit_card_client: credit_card_payment.Client = lagom.injectable,
    ) -> responses.Response:
        reseller_id = ""
        if isinstance(request.user, authentication.AuthenticatedUser):
            reseller_id = request.user.metadata.get("reseller_id", "")

        if voucher:
            payment_intent = await credit_card_client.get_credit_card_payment(
                request.path_params["paymentIntentId"],
                reseller_id,
            )
            intent_amount = money.from_protobuf(payment_intent.amount)
            new_amount = (
                intent_amount.amount - money.from_protobuf(voucher.price).amount
            )
            max_amount = max(
                new_amount,
                orders.MIN_CHARGE[intent_amount.currency.code],
            )
            await credit_card_client.update_credit_card_payment(
                request.path_params["paymentIntentId"],
                reseller_id,
                money.Money(
                    amount=max_amount,
                    currency=intent_amount.currency,
                ),
            )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
