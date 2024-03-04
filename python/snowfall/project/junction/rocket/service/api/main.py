from snowfall.project.junction.go.adapter import (
    errors,
)
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.service import application


async def _http(
    app: application.Application[starlette.Settings],
) -> None:
    asgi_app = starlette.create_starlette_app(
        routes=[],
        openapi_path=None,
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
            settings_class=starlette.Settings,
        ),
    )
