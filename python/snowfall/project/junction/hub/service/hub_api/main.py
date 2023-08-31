from collections.abc import Callable

from starlette import applications, middleware
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
    contacts,
    conversions,
    transactions,
)
from snowfall.project.pay.adapter import (
    companies as companies_adapter,
)
from snowfall.project.pay.service.companies.v1alpha.grpc_pb2_grpc import (
    AccountsServiceStub,
    BeneficiariesServiceStub,
    CompaniesServiceStub,
    ContactsServiceStub,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.service.authentication.v1 import sessions_pb2_grpc
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
    validate_responses_against_spec: bool = True


def _factory(
    app: application.Application[Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        authentication_channel = client.create_channel(
            app.settings.authentication_address,
        )
        session_client = sessions_pb2_grpc.SessionServiceStub(authentication_channel)
        orders_channel = client.create_channel(app.settings.orders_address)
        companies_channel = client.create_channel(app.settings.companies_address)
        transactions_channel = client.create_channel(
            app.settings.transactions_address,
        )
        cc_payment_client = PaymentClient(
            base_url=app.settings.cc_address,
            auth=CurrencyCloudAuth(
                base_url=app.settings.cc_address,
                login_id=app.settings.cc_login,
                api_key=app.settings.cc_api_key,
            ),
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
                    companies_client=companies_adapter.GrpcClient(
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
                    cc_payment_client=cc_payment_client,
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
            validate_response=app.settings.validate_responses_against_spec,
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
        return asgi_app

    return decorator


def _serve(app: application.Application[Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="hub-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=Settings,
        ),
    )
