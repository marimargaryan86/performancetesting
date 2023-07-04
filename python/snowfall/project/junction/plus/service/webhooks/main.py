from collections.abc import Callable

from starlette.applications import Starlette

from snowfall.project.junction.plus.service.webhooks import bootstrap
from snowfall.project.junction.plus.service.webhooks.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], Starlette]:
    def decorator() -> Starlette:
        return application.create_starlette_app(
            router.get_routes(
                bootstrap.create_dependencies(),
            ),
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
