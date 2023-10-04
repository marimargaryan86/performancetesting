from starlette.middleware import Middleware

from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.payments.v1alpha import payments_pb2_grpc
from snowfall.project.pay.service.webhooks import bootstrap, routers
from snowfall.project.pay.service.webhooks.middlewares import HmacHeaderMiddleware
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    payments_channel = create_channel(
        app.settings.payments_address,
    )
    grpc_payment_client = GrpcClient(
        payments_pb2_grpc.PaymentsServiceStub(payments_channel),
    )
    asgi_app = starlette.create_starlette_app(
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

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="webhook")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
