import httpx
from starlette import middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import errors, orders
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.junction.hub.service.hub_api import bootstrap, router
from snowfall.project.pay.adapter import (
    accounts as accounts_adapter,
)
from snowfall.project.pay.adapter import (
    beneficiaries,
    bills,
    companies,
    contacts,
    conversions,
    currencies,
    quotations,
    refunds,
    transactions,
)
from snowfall.project.pay.service.companies.v1alpha.grpc_pb2_grpc import (
    AccountsServiceStub,
    BeneficiariesServiceStub,
    CompaniesServiceStub,
    ContactsServiceStub,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.refunds.v1alpha.grpc_pb2_grpc import (
    RefundsServiceStub,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1alpha.grpc_pb2_grpc import (
    QuotationsServiceStub,
)
from snowfall.service.authentication.v1 import sessions_pb2_grpc
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import client
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


async def _http(app: application.AsyncApplication[Settings]) -> None:
    authentication_channel = client.create_channel(
        app.settings.authentication_address,
    )
    session_client = sessions_pb2_grpc.SessionServiceStub(authentication_channel)
    orders_channel = client.create_channel(app.settings.orders_address)
    companies_channel = client.create_channel(app.settings.companies_address)
    transactions_channel = client.create_channel(app.settings.transactions_address)
    currencies_channel = client.create_channel(app.settings.currencies_address)
    refunds_channel = client.create_channel(app.settings.refunds_address)
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
                        orders_channel,
                    ),
                ),
                accounts_client=accounts_adapter.GrpcClient(
                    AccountsServiceStub(
                        companies_channel,
                    ),
                ),
                companies_client=companies.GrpcClient(
                    CompaniesServiceStub(
                        companies_channel,
                    ),
                ),
                contacts_client=contacts.GrpcClient(
                    ContactsServiceStub(
                        companies_channel,
                    ),
                ),
                beneficiaries_client=beneficiaries.GrpcClient(
                    BeneficiariesServiceStub(
                        companies_channel,
                    ),
                ),
                conversions_client=conversions.GrpcClient(
                    transactions_pb2_grpc.ConversionsServiceStub(
                        transactions_channel,
                    ),
                ),
                transactions_client=transactions.GrpcClient(
                    transactions_pb2_grpc.TransactionsServiceStub(
                        transactions_channel,
                    ),
                ),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        currencies_channel,
                    ),
                ),
                cc_payment_client=cc_payment_client,
                quotations_client=quotations.GrpcClient(
                    QuotationsServiceStub(
                        transactions_channel,
                    ),
                ),
                bills_client=bills.GrpcClient(
                    transactions_pb2_grpc.BillsServiceStub(
                        transactions_channel,
                    ),
                ),
                refunds_client=refunds.GrpcClient(
                    RefundsServiceStub(
                        refunds_channel,
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
