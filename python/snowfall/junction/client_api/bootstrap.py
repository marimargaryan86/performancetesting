from pydantic import BaseSettings
from starlette import applications, exceptions, middleware, routing, status

from snowfall.junction.client_api import handlers, middlewares, routes, validation


class Settings(BaseSettings):
    http_port: int = 8000
    reload: bool = False


def create_app(validator: validation.Validator) -> applications.Starlette:
    app_routes = [
        routing.Route("/health", routes.Health),
    ]
    custom_middlewares = [
        middleware.Middleware(middlewares.ValidationMiddleware, validator=validator),
    ]

    app = applications.Starlette(routes=app_routes, middleware=custom_middlewares)
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app
