import base64
import random
from typing import Callable

import uvicorn
from asgiref.typing import ASGIApplication
from starlette.middleware import Middleware, authentication

from snowfall.adapter import (
    legs,
    offer_searches,
    offers,
    orders,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.junction.client_api import bootstrap, jwt
from snowfall.junction.client_api.routes import router
from snowfall.junction.offers.v1alpha import grpc_pb2_grpc
from snowfall.junction.orders.v1alpha import orders_pb2_grpc
from snowfall.junction.places.v1alpha import places_pb2_grpc
from snowfall.junction.schedules.v1alpha import schedules_pb2_grpc
from snowfall.junction.trips.v1alpha import trips_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        openapi_spec = filesystem.PkgLoader("client_api").load("openapi.json")
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
        forwarded_allow_ips=",".join(
            [
                "*" if str(address) == "0.0.0.0" else str(address)  # nosec
                for address in app.settings.forwarded_allowed_ips
            ],
        ),
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
