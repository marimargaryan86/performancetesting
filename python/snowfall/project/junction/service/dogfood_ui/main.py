from typing import Callable

import httpx
from starlette import applications, routing

from snowfall.project.junction.service.dogfood_ui import routes
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.integration.starlette import routes as stdlib_routes


class _Settings(application.Settings):
    auth_token: str
    base_url: str


def _routes(app: service.Application[_Settings]) -> list[routing.Route]:
    return [
        routing.Route("/", routes.ui),
        stdlib_routes.Proxy(
            httpx.AsyncClient(
                http2=True,
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
    app: service.Application[_Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        return application.create_starlette_app(
            routes=_routes(app),
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
