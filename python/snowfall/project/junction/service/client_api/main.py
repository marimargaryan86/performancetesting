import base64
import random
from typing import Callable

from asgiref.typing import ASGIApplication
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.adapter import (
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.project.junction.service.client_api import bootstrap, jwt
from snowfall.project.junction.service.client_api.routes import router
from snowfall.project.junction.service.offers.v1alpha import grpc_pb2_grpc
from snowfall.project.junction.service.orders.v1alpha import orders_pb2_grpc
from snowfall.project.junction.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.service.schedules.v1alpha import schedules_pb2_grpc
from snowfall.project.junction.service.trips.v1alpha import trips_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        places_channel = create_channel(
            random.choice(app.settings.places_address),  # nosec
        )
        orders_channel = create_channel(
            random.choice(app.settings.orders_address),  # nosec
        )
        offers_channel = create_channel(
            random.choice(app.settings.offers_address),  # nosec
        )
        trips_channel = create_channel(
            random.choice(app.settings.trips_address),  # nosec
        )
        schedules_channel = create_channel(
            random.choice(app.settings.schedules_address),  # nosec
        )

        return application.create_asgi_app(
            routes_factory=router.get_routes,
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=jwt.JWTAuthenticationBackend(
                        token_version=app.settings.jwt_token_version,
                        public_key=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            dependencies=bootstrap.create_dependencies(
                legs_client=legs.GrpcClient(
                    schedules=schedules_pb2_grpc.ScheduleServiceStub(
                        schedules_channel,
                    ),
                ),
                locations_client=locations.GrpcClient(
                    places_pb2_grpc.LocationsServiceStub(places_channel),
                ),
                places_client=places.GrpcClient(
                    places_pb2_grpc.PlacesServiceStub(places_channel),
                ),
                trip_searches_client=trip_searches.GrpcClient(
                    trips=trips_pb2_grpc.TripServiceStub(trips_channel),
                    trip_searches=trips_pb2_grpc.TripSearchServiceStub(
                        trips_channel,
                    ),
                ),
                trips_client=trips.GrpcClient(
                    trips_pb2_grpc.TripServiceStub(trips_channel),
                ),
                offers_client=offers.GrpcClient(
                    offers=grpc_pb2_grpc.OfferServiceStub(offers_channel),
                ),
                offer_searches_client=offer_searches.GrpcClient(
                    offers=grpc_pb2_grpc.OfferServiceStub(offers_channel),
                    offer_searches=grpc_pb2_grpc.OfferSearchServiceStub(
                        offers_channel,
                    ),
                ),
                orders_client=orders.GrpcClient(
                    orders=orders_pb2_grpc.OrderServiceStub(orders_channel),
                ),
                segments_client=segments.GrpcClient(
                    segments=trips_pb2_grpc.TripServiceStub(trips_channel),
                ),
                schedules_client=schedules.GrpcClient(
                    schedules=schedules_pb2_grpc.ScheduleServiceStub(
                        schedules_channel,
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path(
                "junction.client_api",
                "openapi.json",
            ),
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
    entrypoint = service.Entrypoint(name="client-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
