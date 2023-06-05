from typing import Callable

from starlette import applications

from snowfall.project.junction.hub.service.web_api import bootstrap, router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        return application.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(),
            ),
            openapi_path=None,
            security_headers=False,
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
    entrypoint = service.Entrypoint(name="web-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
