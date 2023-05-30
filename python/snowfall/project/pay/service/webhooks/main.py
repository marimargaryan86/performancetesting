from typing import Callable

from lagom.integrations import starlette
from starlette.applications import Starlette

from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.payments.v1alpha import payments_pb2_grpc
from snowfall.project.pay.service.webhooks import boostrap, payments
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[boostrap.Settings],
) -> Callable[[], Starlette]:
    def decorator() -> Starlette:
        payments_channel = create_channel(
            app.settings.payments_address,
        )
        grpc_payment_client = GrpcClient(
            payments_pb2_grpc.PaymentsServiceStub(payments_channel),
        )
        dependencies = boostrap.create_dependencies(payment_client=grpc_payment_client)
        integrations = starlette.StarletteIntegration(dependencies)
        routes = [
            integrations.route("/webhooks/payments", payments.Payment, name="Payments"),
        ]
        return Starlette(routes=routes)

    return decorator


def _serve(app: service.Application[boostrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="webhook")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=boostrap.Settings,
        ),
    )
