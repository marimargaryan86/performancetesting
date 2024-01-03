import ipaddress

import httpx
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.payments.credit_card_service.grpc import (
    CreditCardPaymentService,
)
from snowfall.project.pay.service.payments.grpc import PaymentsService
from snowfall.project.pay.service.payments.providers.stripe.repositories import (
    PaymentUsersRepository,
)
from snowfall.project.pay.service.payments.providers.stripe.stripe import Stripe
from snowfall.project.pay.service.payments.repositories import PaymentsRepository
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50065
    mongo_dsn: AnyUrl
    cc_login: str
    cc_api_key: str
    cc_address: str


class _CreditCardGrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50065
    mongo_dsn: AnyUrl
    stripe_version: str
    stripe_api_key: str


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

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CreditCardPaymentService(  # type: ignore[abstract]
                stripe_provider,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(app.settings.mongo_dsn),
    )
    payment_client = PaymentClient(
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
        client=metrics.register(httpx.AsyncClient()),
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PaymentsService(
                PaymentsRepository(mongo.payments.payments),
                payment_client,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="payments")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="grpc-credit-card",
            callback=_serve_credit_card_payment,
            settings_class=_CreditCardGrpcSettings,
        ),
    )
