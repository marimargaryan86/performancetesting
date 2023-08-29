from collections.abc import Callable

from starlette import applications

from snowfall.project.junction.go.adapter import errors, locations, places
from snowfall.project.junction.go.service.admin_api import bootstrap, router
from snowfall.project.junction.go.service.places.v1 import places_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: application.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
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
            validate_response=app.settings.validate_responses_against_spec,
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

        return asgi_app

    return decorator


def _serve(app: application.Application[bootstrap.Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="admin-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
