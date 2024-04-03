from lagom.integrations.starlette import StarletteIntegration
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.rocket.service.api import (
    bootstrap,
    errors,
)
from snowfall.project.junction.rocket.service.api.air import (
    router as air_router,
)
from snowfall.project.junction.rocket.service.api.car_rental import (
    router as car_rental_router,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    router as hotel_router,
)
from snowfall.project.junction.rocket.service.api.middleware import (
    JunctionOneClientMiddleware,
)
from snowfall.project.junction.rocket.service.api.settings import Settings
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application
from snowfall.vendor.junction_one.auth import TemporaryTokenAuth


async def _http(app: application.Application[Settings]) -> None:
    container = await bootstrap.create_dependencies(app)

    integration = StarletteIntegration(container)

    routes = [
        *air_router.get_routes(integration),
        *hotel_router.get_routes(integration),
        *car_rental_router.get_routes(integration),
    ]

    asgi_app = starlette.create_starlette_app(
        routes=routes,
        custom_middlewares=[
            Middleware(
                cls=authentication.AuthenticationMiddleware,
                backend=container[stdlib_auth.JWTAuthenticationBackend],
                on_error=handlers.auth_error_handler,
            ),
            Middleware(
                JunctionOneClientMiddleware,
                token_auth=container[TemporaryTokenAuth],
            ),
        ],
        openapi_path=filesystem.resource_path(
            "junction.rocket_api",
            "openapi.json",
        ),
    )
    asgi_app.add_exception_handler(
        cursor.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=Settings,
        ),
    )
