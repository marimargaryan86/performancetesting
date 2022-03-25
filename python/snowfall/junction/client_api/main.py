# flake8: noqa: WPS201
import http
import random

import grpc
import uvicorn
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import (
    offer_searches,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.junction.client_api import (
    bootstrap,
    handlers,
    jwt,
    middlewares,
    validation,
)
from snowfall.junction.offers.v1alpha import offers_pb2_grpc
from snowfall.junction.places.v1alpha import places_pb2_grpc
from snowfall.junction.schedules.v1alpha import schedules_pb2_grpc
from snowfall.junction.trips.v1alpha import trips_pb2_grpc
from snowfall.service import make_service
from snowfall.stdlib.persistence import filesystem


def _factory() -> applications.Starlette:
    make_service(name="client-api")
    settings = bootstrap.Settings()
    offers_channel = grpc.aio.insecure_channel(
        random.choice(settings.offers_address),  # nosec
    )
    trips_channel = grpc.aio.insecure_channel(
        random.choice(settings.trips_address),  # nosec
    )
    schedules_channel = grpc.aio.insecure_channel(
        random.choice(settings.schedules_address),  # nosec
    )

    return bootstrap.create_app(
        custom_middlewares=[
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    filesystem.PkgLoader("client_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=jwt.JWTAuthenticationBackend(
                    public_key=settings.jwt_public_key,
                    token_version=settings.jwt_token_version,
                ),
                on_error=handlers.auth_error_handler,
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
            trip_searches_client=trip_searches.GrpcClient(
                trips=trips_pb2_grpc.TripServiceStub(trips_channel),
                trip_searches=trips_pb2_grpc.TripSearchServiceStub(trips_channel),
            ),
            trips_client=trips.GrpcClient(
                trips_pb2_grpc.TripServiceStub(trips_channel),
            ),
            offer_searches_client=offer_searches.GrpcClient(
                offers=offers_pb2_grpc.OfferServiceStub(offers_channel),
                offer_searches=offers_pb2_grpc.OfferSearchServiceStub(offers_channel),
            ),
            segments_client=segments.GrpcClient(
                segments=trips_pb2_grpc.TripServiceStub(trips_channel),
            ),
            schedules_client=schedules.GrpcClient(
                schedules=schedules_pb2_grpc.ScheduleServiceStub(schedules_channel),
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
