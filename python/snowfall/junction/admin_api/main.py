import random
from typing import Callable

import uvicorn
from asgiref.typing import ASGIApplication

from snowfall.adapter import places
from snowfall.junction.admin_api import bootstrap, router
from snowfall.junction.places.v1alpha import places_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        openapi_spec = filesystem.PkgLoader("admin_api").load("openapi.json")
        places_channel = create_channel(
            random.choice(app.settings.places_address),  # nosec
        )

        return application.create_asgi_app(
            routes_factory=router.get_routes,
            dependencies=bootstrap.create_dependencies(
                places_client=places.GrpcClient(
                    places_pb2_grpc.PlacesServiceStub(places_channel),
                ),
            ),
            openapi_specification=openapi_spec,
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    uvicorn.run(
        app=_factory(app),
        factory=True,
        host=str(app.settings.http_address),
        loop="asyncio",
        port=app.settings.http_port,
        access_log=False,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips=[
            "*" if str(address) == "0.0.0.0" else str(address)  # nosec
            for address in app.settings.forwarded_allowed_ips
        ],
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
