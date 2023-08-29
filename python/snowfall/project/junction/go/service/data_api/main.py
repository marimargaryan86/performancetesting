from collections.abc import Callable

from starlette import applications

from snowfall.project.junction.go.service.data_api import bootstrap
from snowfall.project.junction.go.service.data_api.routes import router
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import client as grpc_client


def _factory(
    app: application.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
            grpc_client.create_channel(app.settings.geodata_address),
        )
        return starlette.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    geocoding=geocoder,
                ),
            ),
            openapi_path=filesystem.resource_path(
                "junction.data_api",
                "openapi.json",
            ),
            validate_response=app.settings.validate_responses_against_spec,
        )

    return decorator


def _serve(app: application.Application[bootstrap.Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="data-api")
    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
