from typing import Callable

import currencycloud
from asgiref.typing import ASGIApplication

from snowfall.project.junction.service.pay_api import bootstrap
from snowfall.project.junction.service.pay_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem

_SERVICE_NAME = "pay-api"


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        cc_client = currencycloud.Client(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        )
        return application.create_asgi_app(
            routes_factory=router.get_routes,
            dependencies=bootstrap.create_dependencies(cc_client),
            openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
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
    entrypoint = service.Entrypoint(name="pay-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
