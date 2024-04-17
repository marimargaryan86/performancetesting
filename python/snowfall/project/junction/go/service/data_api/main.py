from snowfall.project.junction.go.service.data_api import bootstrap
from snowfall.project.junction.go.service.data_api.routes import router
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
    )
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                geocoding=geocoder,
            ),
        ),
        openapi_path=filesystem.resource_path(
            "junction.data_api",
            "openapi.yaml",
        ),
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-go-data-api")
    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
