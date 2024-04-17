import ipaddress

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.payments.credit_card_service.grpc import (
    CreditCardPaymentService,
)
from snowfall.project.pay.service.payments.invoice_service.grpc import InvoiceService
from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.providers.stripe.repositories import (
    PaymentUsersRepository,
)
from snowfall.project.pay.service.payments.providers.stripe.stripe import Stripe
from snowfall.project.pay.service.payments.providers.stripe_invoice.client import (
    StripeInvoice,
)
from snowfall.project.pay.service.payments.providers.stripe_mock.stripe import (
    MockStripe,
)
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server


class _CreditCardGrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50065
    mongo_dsn: AnyUrl
    stripe_version: str
    stripe_api_key: str
    payment_provider_resellers: dict[str, str]


async def _serve_credit_card_payment(
    app: application.Application[_CreditCardGrpcSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(app.settings.mongo_dsn),
    )
    payment_users_repository = PaymentUsersRepository(
        mongo.payments.stripe_users,
    )
    stripe_provider = Stripe(
        payment_users_repository,
        app.settings.stripe_version,
        app.settings.stripe_api_key,
    )
    mock_stripe_provider = MockStripe()
    stripe_invoice_provider = StripeInvoice(
        app.settings.stripe_version,
        app.settings.stripe_api_key,
    )
    providers: dict[str, interfaces.CreditCardProvider] = {
        stripe_provider.name: stripe_provider,
        mock_stripe_provider.name: mock_stripe_provider,
    }

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CreditCardPaymentService(
                providers,
                app.settings.payment_provider_resellers,
            ),
            InvoiceService(
                stripe_invoice_provider,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="pay-payments")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc-credit-card",
            callback=_serve_credit_card_payment,
            settings_class=_CreditCardGrpcSettings,
        ),
    )
