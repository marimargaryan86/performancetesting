from collections.abc import Callable

from starlette.applications import Starlette
from starlette.middleware import Middleware

from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.payments.v1alpha import payments_pb2_grpc
from snowfall.project.pay.service.webhooks import bootstrap, routers
from snowfall.project.pay.service.webhooks.middlewares import HmacHeaderMiddleware
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: application.Application[bootstrap.Settings],
) -> Callable[[], Starlette]:
    def decorator() -> Starlette:
        payments_channel = create_channel(
            app.settings.payments_address,
        )
        grpc_payment_client = GrpcClient(
            payments_pb2_grpc.PaymentsServiceStub(payments_channel),
        )
        return starlette.create_starlette_app(
            routes=routers.get_routes(
                bootstrap.create_dependencies(
                    payment_client=grpc_payment_client,
                ),
            ),
            custom_middlewares=[
                Middleware(HmacHeaderMiddleware, secret_key=app.settings.secret_key),
            ],
            openapi_path=None,
        )

    return decorator


def _serve(app: application.Application[bootstrap.Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="webhook")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
