from collections.abc import Callable

import httpx
import lagom
from lagom.integrations import starlette as starlette_integration
from starlette import applications, routing, staticfiles, templating

from snowfall.project.junction.go.service.dogfood_ui import routes
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import routes as stdlib_routes
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application


class _Settings(starlette.Settings):
    auth_token: str
    base_url: str


def _routes(app: application.Application[_Settings]) -> list[routing.BaseRoute]:
    container = lagom.Container()
    container[templating.Jinja2Templates] = templating.Jinja2Templates(
        filesystem.package_path(
            "snowfall.project.junction.go.service.dogfood_ui.templates",
        ),
    )

    integration = starlette_integration.StarletteIntegration(container)

    return [
        integration.route("/", routes.UI),
        routing.Mount(
            "/static",
            staticfiles.StaticFiles(
                html=False,
                packages=[
                    ("snowfall.project.junction.go.service.dogfood_ui.main", "static"),
                ],
            ),
        ),
        stdlib_routes.Proxy(
            httpx.AsyncClient(
                base_url=app.settings.base_url,
                headers={
                    "Accept": "application/vnd.api+json",
                    "Authorization": "Bearer {0}".format(app.settings.auth_token),
                    "Content-Type": "application/vnd.api+json",
                    "User-Agent": app.user_agent,
                },
            ),
        ).to_route(),
    ]


def _factory(
    app: application.Application[_Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        return starlette.create_starlette_app(
            routes=_routes(app),
            openapi_path=None,
            security_headers=False,
        )

    return decorator


def _serve(app: application.Application[_Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="dogfood-ui")

    entrypoint.enter_with_commands(
        application.Command(name="http", callback=_serve, settings_class=_Settings),
    )
