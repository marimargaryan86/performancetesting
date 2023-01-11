import base64
import random
from typing import Callable

import currencycloud
from motor import motor_asyncio
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.adapter import authentication as auth
from snowfall.project.junction.adapter import currencies, errors
from snowfall.project.junction.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.junction.service.pay_api import authenticator, bootstrap
from snowfall.project.junction.service.pay_api.repositories import CompanyRepository
from snowfall.project.junction.service.pay_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc.client import create_channel

_SERVICE_NAME = "pay-api"


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        orders_channel = create_channel(
            random.choice(app.settings.currencies_address),  # nosec
        )
        authentication_channel = create_channel(
            app.settings.authentication_address,
        )
        cc_client = currencycloud.Client(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        )
        mongo = motor_asyncio.AsyncIOMotorClient(
            app.settings.mongo_dsn,
        )
        asgi_app = application.create_starlette_app(
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=authenticator.Authenticator(
                        public_key_content=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    cc_client=cc_client,
                    currencies_client=currencies.GrpcClient(
                        currencies_pb2_grpc.CurrencyServiceStub(orders_channel),
                    ),
                    authentication_client=auth.GrpcClient(
                        auth.auth_pb2_grpc.AuthenticationServiceStub(
                            authentication_channel,
                        ),
                    ),
                    companies_repository=CompanyRepository(
                        mongo.companies.companies,
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
        )

        asgi_app.add_exception_handler(
            errors.CursorError,
            handlers.cursor_error_handler,
        )
        asgi_app.add_exception_handler(
            errors.NotFoundError,
            handlers.not_found_error_handler,
        )
        asgi_app.add_exception_handler(
            errors.ServiceUnavailableError,
            handlers.service_unavailable_error_handler,
        )

        return asgi_app

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="pay-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
