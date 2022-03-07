import http
import random

import grpc
import uvicorn
from starlette import applications, middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from snowfall.adapter import offer_searches, places, trip_searches
from snowfall.filesystem import loaders
from snowfall.junction.client_api import bootstrap, middlewares, patch, validation
from snowfall.junction.offers.v1alpha import offers_pb2_grpc
from snowfall.junction.places.v1alpha import places_pb2_grpc
from snowfall.service import make_service


def _factory() -> applications.Starlette:
    make_service(name="client-api")
    settings = bootstrap.Settings()
    offers_channel = grpc.aio.insecure_channel(
        random.choice(settings.offers_address),  # nosec
    )

    return bootstrap.create_app(
        custom_middlewares=[
            middleware.Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    loaders.PkgLoader("client_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            middleware.Middleware(
                AuthenticationMiddleware,
                backend=patch.JWTAuthenticationBackend(patch.AuthSettings()),
            ),
        ],
        dependencies=bootstrap.create_dependencies(
            places_client=places.GrpcClient(
                places_pb2_grpc.PlacesServiceStub(
                    grpc.aio.insecure_channel(
                        random.choice(settings.places_address),  # nosec
                    ),
                ),
            ),
            trip_searches_client=trip_searches.DictClient(),
            offer_searches_client=offer_searches.GrpcClient(
                offers=offers_pb2_grpc.OfferServiceStub(offers_channel),
                offer_searches=offers_pb2_grpc.OfferSearchServiceStub(offers_channel),
            ),
        ),
    )


if __name__ == "__main__":
    _settings = bootstrap.Settings()

    uvicorn.run(
        app="snowfall.junction.client_api.main:_factory",
        factory=True,
        host=str(_settings.http_address),
        port=_settings.http_port,
        access_log=False,
        reload=_settings.reload,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips=[
            str(address) for address in _settings.forwarded_allowed_ips
        ],
    )
