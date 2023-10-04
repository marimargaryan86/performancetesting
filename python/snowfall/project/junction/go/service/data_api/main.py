from snowfall.project.junction.go.service.data_api import bootstrap
from snowfall.project.junction.go.service.data_api.routes import router
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import client as grpc_client


async def _http(
    app: application.AsyncApplication[bootstrap.Settings],
) -> None:
    geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
        grpc_client.create_channel(app.settings.geodata_address),
    )
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                geocoding=geocoder,
            ),
        ),
        openapi_path=filesystem.resource_path(
            "junction.data_api",
            "openapi.json",
        ),
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="data-api")
    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
