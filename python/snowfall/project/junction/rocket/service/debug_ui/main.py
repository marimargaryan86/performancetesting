import base64
import functools
import hashlib

import jinja2
from starlette import routing, staticfiles, templating

from snowfall.project.junction.go.service.places.v1 import places_pb2_grpc
from snowfall.project.junction.go.service.planner.v1 import planner_pb2_grpc
from snowfall.project.junction.rocket.service.debug_ui import endpoints
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import routes as stdlib_routes
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory


class _Settings(starlette.Settings):
    places_address: str
    planner_address: str


@functools.cache
def _hash_static_resources() -> dict[str, str]:
    hashes = {}
    static_path = filesystem.package_path(
        "snowfall.project.junction.rocket.service.debug_ui.main",
    )

    for static_file_path in static_path.glob("static/*"):
        if static_file_path.is_dir():
            continue

        with static_file_path.open("rb", buffering=0) as static_file:
            hashes[static_file_path.name] = base64.urlsafe_b64encode(
                hashlib.file_digest(
                    static_file,  # type: ignore[arg-type]
                    "sha512",
                ).digest(),
            ).decode()

    return hashes


async def _routes(app: application.Application[_Settings]) -> list[routing.BaseRoute]:
    loader = jinja2.PackageLoader(
        package_name="snowfall.project.junction.rocket.service.debug_ui.main",
    )

    places_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.places_address,
    )
    planner_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.planner_address,
    )

    environment = jinja2.Environment(loader=loader, autoescape=True)
    templates = templating.Jinja2Templates(env=environment)
    locations = endpoints.Locations(
        locations=places_pb2_grpc.LocationsServiceStub(places_channel),
    )
    places = endpoints.Places(
        places=places_pb2_grpc.PlacesServiceStub(places_channel),
    )
    routes = endpoints.Routes(
        planner=planner_pb2_grpc.PlannerServiceStub(planner_channel),
    )
    ui = endpoints.UI(templates, _hash_static_resources())

    return [
        stdlib_routes.to_route(
            "/locations/near",
            locations.post_near,
            methods=["POST"],
        ),
        stdlib_routes.to_route("/locations", locations.post, methods=["POST"]),
        stdlib_routes.to_route("/places", places.post, methods=["POST"]),
        stdlib_routes.to_route("/routes", routes.post, methods=["POST"]),
        stdlib_routes.to_route("/", ui.get),
        routing.Mount(
            "/static",
            staticfiles.StaticFiles(
                html=False,
                packages=[
                    (
                        "snowfall.project.junction.rocket.service.debug_ui.main",
                        "static",
                    ),
                ],
            ),
        ),
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
    entrypoint = application.Entrypoint(name="junction-rocket-debug-ui")

    entrypoint.enter_with_commands(
        application.Command(name="http", callback=_http, settings_class=_Settings),
    )
