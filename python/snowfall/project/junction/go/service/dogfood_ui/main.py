import httpx
import lagom
import pydantic
from lagom.integrations import starlette as starlette_integration
from starlette import routing, staticfiles, templating

from snowfall.project.junction.go.service.dogfood_ui import routes
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import routes as stdlib_routes
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, httpx_factory


class _Settings(starlette.Settings):
    auth_token: str
    base_url: pydantic.AnyHttpUrl


async def _routes(app: application.Application[_Settings]) -> list[routing.BaseRoute]:
    container = lagom.Container()
    container[templating.Jinja2Templates] = templating.Jinja2Templates(
        filesystem.package_path(
            "snowfall.project.junction.go.service.dogfood_ui.templates",
        ),
    )
    container[httpx.AsyncClient] = await httpx_factory.make_client(
        app=app,
        base_url=app.settings.base_url,
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": "Bearer {0}".format(app.settings.auth_token),
            "Content-Type": "application/vnd.api+json",
        },
    )

    integration = starlette_integration.StarletteIntegration(container)

    return [
        integration.route("/", routes.UI),
        integration.route("/locations", routes.Locations),
        routing.Mount(
            "/static",
            staticfiles.StaticFiles(
                html=False,
                packages=[
                    ("snowfall.project.junction.go.service.dogfood_ui.main", "static"),
                ],
            ),
        ),
        stdlib_routes.Proxy(container[httpx.AsyncClient]).to_route(),
    ]


async def _http(
    app: application.Application[_Settings],
) -> None:
    asgi_app = starlette.create_starlette_app(
        routes=await _routes(app),
        openapi_path=None,
        security_headers=False,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-go-dogfood-ui")

    entrypoint.enter_with_commands(
        application.Command(name="http", callback=_http, settings_class=_Settings),
    )
