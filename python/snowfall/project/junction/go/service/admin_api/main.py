from snowfall.project.junction.go.adapter import errors, locations, places
from snowfall.project.junction.go.service.admin_api import bootstrap, router
from snowfall.project.junction.go.service.places.v1 import places_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


async def _http(
    app: application.AsyncApplication[bootstrap.Settings],
) -> None:
    places_channel = create_channel(app.settings.places_address)

    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                locations_client=locations.GrpcClient(
                    places_pb2_grpc.LocationsServiceStub(places_channel),
                ),
                places_client=places.GrpcClient(
                    places_pb2_grpc.PlacesServiceStub(places_channel),
                ),
            ),
        ),
        openapi_path=filesystem.resource_path("junction.admin_api", "openapi.json"),
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

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="admin-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
