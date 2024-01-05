import lagom
import stripe
from starlette import endpoints, requests

from snowfall.adapter import identities as identities_adapter
from snowfall.project.junction.go.adapter import resellers as resellers_adapter
from snowfall.project.junction.hub.service.hub_api.routes import routes_handlers
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    request_helpers,
)

_stripe_version = "2020-08-27"


class Payments(endpoints.HTTPEndpoint):
    @routes_handlers.grpc_errors_handler
    async def post(
        self,
        request: requests.Request,
        companies_client: companies_adapter.Client = lagom.injectable,
        resellers_client: resellers_adapter.Client = lagom.injectable,
        identities_client: identities_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        stripe_id: str = request.user.metadata.get("stripe_customer_id", "")
        if not stripe_id:
            reseller_id = request.user.metadata.get("reseller_id", "")
            reseller = await resellers_client.get_reseller(reseller_id)
            company = await companies_client.get(reseller.company_id)

            stripe_id = stripe.Customer.create(
                name=company.name,
                email=request.user.email,
                address={
                    "line1": company.address.address_lines[0],
                    "line2": company.address.address_lines[1],
                    "city": company.address.locality,
                    "country": company.address.region_code,
                    "postal_code": company.address.postal_code,
                },
            ).id

            await identities_client.update_ory_identity(
                identifier=request.user.identifier,
                email=request.user.email,
                metadata={**request.user.metadata, "stripe_customer_id": stripe_id},
            )

        body = await request_helpers.flatten_request(request)

        intent_money = money.from_string(
            body["amount"],
            money.Currency(body["currency"]),
        )

        ephemeral_key_secret: str = stripe.EphemeralKey.create(
            # type: ignore[no-untyped-call]
            customer=stripe_id,
            stripe_version=_stripe_version,
        ).secret

        intent = stripe.PaymentIntent.create(
            amount=intent_money.amount,
            currency=intent_money.currency.code,
            capture_method="manual",
            customer=stripe_id,
            setup_future_usage="on_session",
            automatic_payment_methods={
                "enabled": True,
            },
        )

        attributes = {
            "clientSecret": intent.client_secret,
            "ephemeralKey": ephemeral_key_secret,
        }

        attributes = {
            key: attr_value
            for key, attr_value in attributes.items()
            if attr_value is not None
        }

        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=intent.stripe_id or "",
                    type="payments",
                    attributes=attributes,
                    relationships={
                        "stripeCustomer": {
                            "data": models.ResourceIdentifier(
                                id=stripe_id,
                                type="stripe-customer",
                            ),
                        },
                    },
                ),
            ),
            request=request,
        )
