from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.service import application


async def _http(app: application.Application[starlette.Settings]) -> None:
    asgi_app = starlette.create_starlette_app(
        routes=[],
        openapi_path=None,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="zendesk-webhook")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=starlette.Settings,
        ),
    )
