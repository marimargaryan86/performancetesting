from collections.abc import Callable

from starlette.applications import Starlette
from starlette.middleware import Middleware
from twilio.request_validator import RequestValidator

from snowfall.project.junction.plus.adapter import monitoring_rules
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.plus_webhooks import (
    bootstrap,
    middlewares,
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], Starlette]:
    def decorator() -> Starlette:
        return application.create_starlette_app(
            router.get_routes(
                bootstrap.create_dependencies(
                    monitoring_rules_client=monitoring_rules.GrpcClient(
                        monitoring_rules=notifications_pb2_grpc.MonitoringRuleServiceStub(
                            create_channel(app.settings.notifications_address),
                        ),
                    ),
                ),
            ),
            custom_middlewares=[
                Middleware(
                    middlewares.HmacHeaderMiddleware,
                    secret_key=app.settings.flight_stats_app_key,
                    twilio_validator=RequestValidator(app.settings.twilio_token),
                ),
            ],
            openapi_path=None,
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="plus-webhook")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
