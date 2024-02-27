import asyncio
from typing import NamedTuple

from grpc import aio
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import (
    errors,
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    places,
    price_quotes,
    schedules,
    segments,
    trip_candidate_searches,
    trip_candidates,
    trip_searches,
    trips,
)
from snowfall.project.junction.go.service.bridge.v1alpha import (
    trips_pb2_grpc as bridge_trips_pb2_grpc,
)
from snowfall.project.junction.go.service.client_api import (
    authentication as authentication_backends,
)
from snowfall.project.junction.go.service.client_api import (
    bootstrap,
    router,
)
from snowfall.project.junction.go.service.offers.v1 import grpc_pb2_grpc
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.junction.go.service.places.v1 import places_pb2_grpc
from snowfall.project.junction.go.service.schedules.v1 import schedules_pb2_grpc
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2_grpc
from snowfall.service.authentication.v1 import authentication_pb2_grpc, oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application, grpc_factory


class _Channels(NamedTuple):
    places: aio.Channel
    orders: aio.Channel
    offers: aio.Channel
    trips: aio.Channel
    bridge: aio.Channel
    schedules: aio.Channel
    authentication: aio.Channel


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    channels = _Channels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(
                app,
                app.settings.places_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.orders_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.offers_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.trips_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.bridge_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.schedules_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.authentication_address,
            ),
        ),
    )
    oath_client = oauth_pb2_grpc.OAuthServiceStub(
        channels.authentication,
    )

    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                authentication_client=auth_adapter.GrpcClient(
                    authentication_pb2_grpc.AuthenticationServiceStub(
                        channels.authentication,
                    ),
                ),
                legs_client=legs.GrpcClient(
                    schedules=schedules_pb2_grpc.ScheduleServiceStub(
                        channels.schedules,
                    ),
                ),
                locations_client=locations.GrpcClient(
                    places_pb2_grpc.LocationsServiceStub(channels.places),
                ),
                places_client=places.GrpcClient(
                    places_pb2_grpc.PlacesServiceStub(channels.places),
                ),
                price_quotes_client=price_quotes.GrpcClient(
                    price_quotes=grpc_pb2_grpc.PriceQuoteServiceStub(
                        channels.offers,
                    ),
                ),
                trip_searches_client=trip_searches.GrpcClient(
                    trips=trips_pb2_grpc.TripServiceStub(channels.trips),
                    trip_searches=trips_pb2_grpc.TripSearchServiceStub(
                        channels.trips,
                    ),
                ),
                trips_client=trips.GrpcClient(
                    trips_pb2_grpc.TripServiceStub(channels.trips),
                ),
                trip_candidate_searches_client=trip_candidate_searches.GrpcBridgeClient(
                    trip_candidate_searches=bridge_trips_pb2_grpc.TripCandidateSearchServiceStub(
                        channels.bridge,
                    ),
                )
                if app.settings.use_bridge
                else trip_candidate_searches.GrpcClient(
                    trip_candidate_searches=trips_pb2_grpc.TripCandidateSearchServiceStub(
                        channels.trips,
                    ),
                ),
                trip_candidates_client=trip_candidates.GrpcClient(
                    trip_candidates=trips_pb2_grpc.TripCandidateServiceStub(
                        channels.trips,
                    ),
                ),
                offers_client=offers.GrpcClient(
                    offers=grpc_pb2_grpc.OfferServiceStub(channels.offers),
                ),
                offer_searches_client=offer_searches.GrpcClient(
                    offer_searches=grpc_pb2_grpc.OfferSearchServiceStub(
                        channels.offers,
                    ),
                ),
                orders_client=orders.GrpcClient(
                    orders=orders_pb2_grpc.OrderServiceStub(channels.orders),
                ),
                segments_client=segments.GrpcClient(
                    segments=trips_pb2_grpc.TripServiceStub(channels.trips),
                ),
                schedules_client=schedules.GrpcClient(
                    schedules=schedules_pb2_grpc.ScheduleServiceStub(
                        channels.schedules,
                    ),
                ),
            ),
            reseller_currencies=app.settings.reseller_currencies,
            reseller_pay_companies=app.settings.reseller_pay_companies,
        ),
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=stdlib_auth.JWTAuthenticationBackend(
                    stdlib_auth.OryAuth(
                        jwk_client=jwt.AsyncJWKClient(
                            jwk_url=auth_adapter.get_jwk_url(
                                app.settings.authentication_address,
                            ),
                            key_ttl=app.settings.ory_jwk_ttl,
                        ),
                        legacy_fallback=authentication_backends.LegacyAuth(
                            jwt_version=app.settings.jwt_token_version,
                            decoder=jwt.Decoder(
                                public_key=app.settings.jwt_public_key,
                                algorithms=["RS256"],
                            ),
                        ).get_reseller_id_from_jwt,
                        client_resolver=auth_adapter.oauth_client_resolver(
                            oauth_client=oath_client,
                        ),
                    ).get_owner_from_jwt,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        openapi_path=filesystem.resource_path(
            "junction.client_api",
            "openapi.json",
        ),
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
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="client-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
