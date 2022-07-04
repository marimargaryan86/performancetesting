from typing import Callable

import currencycloud
import uvicorn
from asgiref.typing import ASGIApplication

from snowfall.junction.pay_api import bootstrap
from snowfall.junction.pay_api.routes import router
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
            openapi_path=filesystem.resource_path("pay_api", "openapi.json"),
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    uvicorn.run(
        app=_factory(app),
        factory=True,
        host=str(app.settings.http_address),
        loop="asyncio",
        port=app.settings.http_port,
        access_log=False,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips=[
            "*" if str(address) == "0.0.0.0" else str(address)  # nosec
            for address in app.settings.forwarded_allowed_ips
        ],
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
