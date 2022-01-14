import random

import grpc
import uvicorn
from starlette import applications

from snowfall.adapter import places
from snowfall.junction.client_api import bootstrap, journeys, loaders, patch, validation
from snowfall.junction.places.v1alpha import places_pb2_grpc
from snowfall.service import make_service


def _factory() -> applications.Starlette:
    make_service(name="client-api")
    patch.patch_open_api()
    settings = bootstrap.Settings()

    return bootstrap.create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
        dependencies=bootstrap.create_dependencies(
            places_client=places.GrpcClient(
                places_pb2_grpc.PlacesServiceStub(
                    grpc.aio.insecure_channel(
                        random.choice(settings.places_address),  # nosec
                    ),
                ),
            ),
            journey_search_repository=journeys.JourneySearchRepository(),
        ),
    )


if __name__ == "__main__":
    _settings = bootstrap.Settings()

    uvicorn.run(
        app="snowfall.junction.client_api.main:_factory",
        factory=True,
        host=_settings.http_address,
        port=_settings.http_port,
        access_log=False,
        reload=_settings.reload,
        log_config=None,
    )
