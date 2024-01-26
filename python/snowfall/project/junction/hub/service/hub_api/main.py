import asyncio
from typing import NamedTuple

import httpx
import stripe
from grpc import aio
from starlette import middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.adapter import authentication as auth_adapter
from snowfall.adapter import identities
from snowfall.project.junction.go.adapter import errors, orders, resellers
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.junction.go.service.resellers.v1 import resellers_pb2_grpc
from snowfall.project.junction.hub.service.hub_api import bootstrap, permissions, router
from snowfall.project.pay.adapter import (
    accounts as accounts_adapter,
)
from snowfall.project.pay.adapter import (
    beneficiaries,
    bills,
    companies,
    contacts,
    conversions,
    credit_card_payment,
    currencies,
    quotations,
    refunds,
    transactions,
)
from snowfall.project.pay.service.companies.v1.grpc_pb2_grpc import (
    AccountsServiceStub,
    BeneficiariesServiceStub,
    CompaniesServiceStub,
    ContactsServiceStub,
)
from snowfall.project.pay.service.currencies.v1 import currencies_pb2_grpc
from snowfall.project.pay.service.payments.v1.credit_card_pb2_grpc import (
    CreditCardPaymentServiceStub,
)
from snowfall.project.pay.service.refunds.v1.grpc_pb2_grpc import (
    RefundsServiceStub,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1.grpc_pb2_grpc import (
    QuotationsServiceStub,
)
from snowfall.service.authentication.v1 import identities_pb2_grpc, sessions_pb2_grpc
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class Settings(starlette.Settings):
    cc_login: str
    cc_api_key: str
    cc_address: str
    authentication_address: str
    orders_address: str
    companies_address: str
    transactions_address: str
    currencies_address: str
    refunds_address: str
    resellers_address: str
    stripe_api_key: str
    credit_card_address: str


class _Channels(NamedTuple):
    orders: aio.Channel
    companies: aio.Channel
    transactions: aio.Channel
    currencies: aio.Channel
    refunds: aio.Channel
    resellers: aio.Channel
    credit_card_payments: aio.Channel


async def _http(app: application.Application[Settings]) -> None:
    stripe.api_key = app.settings.stripe_api_key
    authentication_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.authentication_address,
    )
    session_client = sessions_pb2_grpc.SessionServiceStub(authentication_channel)
    channels = _Channels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(
                app,
                app.settings.orders_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.companies_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.transactions_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.currencies_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.refunds_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.resellers_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.credit_card_address,
            ),
        ),
    )
    cc_payment_client = PaymentClient(
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
        client=metrics.register(httpx.AsyncClient()),
    )

    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                orders_client=orders.GrpcClient(
                    orders_pb2_grpc.OrderServiceStub(
                        channels.orders,
                    ),
                ),
                accounts_client=accounts_adapter.GrpcClient(
                    AccountsServiceStub(
                        channels.companies,
                    ),
                ),
                companies_client=companies.GrpcClient(
                    CompaniesServiceStub(
                        channels.companies,
                    ),
                ),
                contacts_client=contacts.GrpcClient(
                    ContactsServiceStub(
                        channels.companies,
                    ),
                ),
                beneficiaries_client=beneficiaries.GrpcClient(
                    BeneficiariesServiceStub(
                        channels.companies,
                    ),
                ),
                conversions_client=conversions.GrpcClient(
                    transactions_pb2_grpc.ConversionsServiceStub(
                        channels.transactions,
                    ),
                ),
                transactions_client=transactions.GrpcClient(
                    transactions_pb2_grpc.TransactionsServiceStub(
                        channels.transactions,
                    ),
                ),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        channels.currencies,
                    ),
                ),
                cc_payment_client=cc_payment_client,
                quotations_client=quotations.GrpcClient(
                    QuotationsServiceStub(
                        channels.transactions,
                    ),
                ),
                bills_client=bills.GrpcClient(
                    transactions_pb2_grpc.BillsServiceStub(
                        channels.transactions,
                    ),
                ),
                identities_client=identities.GrpcClient(
                    identities_pb2_grpc.IdentitiesServiceStub(
                        authentication_channel,
                    ),
                ),
                refunds_client=refunds.GrpcClient(
                    RefundsServiceStub(
                        channels.refunds,
                    ),
                ),
                resellers_client=resellers.GrpcClient(
                    resellers_pb2_grpc.ResellerServiceStub(
                        channels.resellers,
                    ),
                ),
                credit_card_payment_client=credit_card_payment.GrpcClient(
                    CreditCardPaymentServiceStub(
                        channels.credit_card_payments,
                    ),
                ),
            ),
        ),
        openapi_path=filesystem.resource_path("junction.hub_api", "openapi.json"),
        custom_middlewares=[
            middleware.Middleware(
                auth_middleware.AuthenticationMiddleware,
                backend=authentication.CookieAuthenticationBackend(
                    cookie_to_user=auth_adapter.session_cookie_resolver(
                        session_client=session_client,
                    ),
                ),
                on_error=handlers.auth_error_handler,
            ),
            middleware.Middleware(permissions.PermissionsMiddleware),
        ],
        security_headers=False,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ForbiddenError,
        handlers.forbidden_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="hub-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=Settings,
        ),
    )
