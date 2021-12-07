from starlette import applications, exceptions, middleware, status

from snowfall.junction.client_api import handlers, middlewares, validation


def create_app(validator: validation.Validator) -> applications.Starlette:
    custom_middlewares = [
        middleware.Middleware(middlewares.ValidationMiddleware, validator=validator),
    ]

    app = applications.Starlette(middleware=custom_middlewares)
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app
