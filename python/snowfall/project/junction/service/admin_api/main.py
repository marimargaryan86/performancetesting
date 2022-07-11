import random
from typing import Callable

from asgiref.typing import ASGIApplication

from snowfall.project.junction.adapter import locations, places
from snowfall.project.junction.service.admin_api import bootstrap, router
from snowfall.project.junction.service.places.v1alpha import places_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        places_channel = create_channel(
            random.choice(app.settings.places_address),  # nosec
        )

        return application.create_asgi_app(
            routes_factory=router.get_routes,
            dependencies=bootstrap.create_dependencies(
                locations_client=locations.GrpcClient(
                    places_pb2_grpc.LocationsServiceStub(places_channel),
                ),
                places_client=places.GrpcClient(
                    places_pb2_grpc.PlacesServiceStub(places_channel),
                ),
            ),
            openapi_path=filesystem.resource_path("junction.admin_api", "openapi.json"),
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="admin-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
