from typing import Callable

from fastapi import FastAPI
from starlette import applications

from snowfall.project.pss.service.pss_api_v2.exception_handlers import add_handlers
from snowfall.project.pss.service.pss_api_v2.routes import api_router
from snowfall.project.pss.service.pss_api_v2.settings import Settings
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application


def _factory() -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        fastapi_app = FastAPI(
            title="PSS API",
            description="The new api for PSS",
            version="V2.0.0",
        )
        fastapi_app.include_router(api_router.router)
        add_handlers(fastapi_app)
        return fastapi_app

    return decorator


def _serve(app: service.Application[Settings]) -> None:
    application.serve(
        factory=_factory(),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="api")
    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=Settings,
        ),
    )
