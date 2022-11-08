from typing import Callable

import httpx
import lagom
from lagom.integrations import starlette
from starlette import applications, routing

from snowfall.project.junction.service.dogfood_ui import routes
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.integration.starlette import routes as stdlib_routes
from snowfall.stdlib.persistence import filesystem


class _Settings(application.Settings):
    auth_token: str
    base_url: str


def _dependencies(
    app: service.Application[_Settings],
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    layout_path = filesystem.resource_path(
        "snowfall.project.junction.service.dogfood_ui.routes",
        "layout.html",
    )

    with open(layout_path) as template:
        layout = str(template.read())

    container[routes.Template] = routes.Template(html=layout)
    container[httpx.AsyncClient] = httpx.AsyncClient(
        base_url=app.settings.base_url,
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": "Bearer {0}".format(app.settings.auth_token),
            "Content-Type": "application/vnd.api+json",
            "User-Agent": app.user_agent,
        },
    )

    return starlette.StarletteIntegration(container)


def _routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/", routes.UI),
        stdlib_routes.Proxy(
            dependencies._container[httpx.AsyncClient],  # noqa: WPS437
        ).to_route(),
    ]


def _factory(
    app: service.Application[_Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        return application.create_starlette_app(
            routes_factory=_routes,
            dependencies=_dependencies(app),
            openapi_path=None,
        )

    return decorator


def _serve(app: service.Application[_Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="dogfood-ui")

    entrypoint.enter_with_commands(
        service.Command(name="http", callback=_serve, settings_class=_Settings),
    )
