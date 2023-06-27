from collections.abc import Callable

import httpx
from starlette import applications
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
from snowfall.project.junction.go.service.client_api import (
    authentication as authentication_backends,
)
from snowfall.project.junction.go.service.client_api import bootstrap, router
from snowfall.project.junction.go.service.offers.v1 import grpc_pb2_grpc
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.junction.go.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.go.service.schedules.v1alpha import schedules_pb2_grpc
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2_grpc
from snowfall.service.authentication.v1alpha import authentication_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.stdlib.transport.http import auth


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        places_channel = create_channel(app.settings.places_address)
        orders_channel = create_channel(app.settings.orders_address)
        offers_channel = create_channel(app.settings.offers_address)
        trips_channel = create_channel(app.settings.trips_address)
        schedules_channel = create_channel(app.settings.schedules_address)
        authentication_channel = create_channel(app.settings.authentication_address)

        asgi_app = application.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    authentication_client=auth_adapter.GrpcClient(
                        authentication_pb2_grpc.AuthenticationServiceStub(
                            authentication_channel,
                        ),
                    ),
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
                    price_quotes_client=price_quotes.GrpcClient(
                        price_quotes=grpc_pb2_grpc.PriceQuoteServiceStub(
                            offers_channel,
                        ),
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
                    trip_candidate_searches_client=trip_candidate_searches.GrpcClient(
                        trip_candidate_searches=trips_pb2_grpc.TripCandidateSearchServiceStub(
                            trips_channel,
                        ),
                    ),
                    trip_candidates_client=trip_candidates.GrpcClient(
                        trip_candidates=trips_pb2_grpc.TripCandidateServiceStub(
                            trips_channel,
                        ),
                    ),
                    offers_client=offers.GrpcClient(
                        offers=grpc_pb2_grpc.OfferServiceStub(offers_channel),
                    ),
                    offer_searches_client=offer_searches.GrpcClient(
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
                reseller_currencies=app.settings.reseller_currencies,
                reseller_pay_companies=app.settings.reseller_pay_companies,
            ),
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=stdlib_auth.JWTAuthenticationBackend(
                        stdlib_auth.OryAuth(
                            jwk_client=jwt.AsyncJWKClient(
                                base_url=app.settings.ory_application_url,
                                key_ttl=app.settings.ory_jwk_ttl,
                            ),
                            legacy_fallback=authentication_backends.LegacyAuth(
                                jwt_version=app.settings.jwt_token_version,
                                decoder=jwt.Decoder(
                                    public_key=app.settings.jwt_public_key,
                                    algorithms=["RS256"],
                                ),
                            ).get_reseller_id_from_jwt,
                            client=httpx.AsyncClient(
                                base_url=app.settings.ory_application_url,
                                auth=auth.TokenAuth(token=app.settings.ory_api_key),
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
        asgi_app.add_exception_handler(
            errors.UnprocessableEntityError,
            handlers.unprocessable_entity_error_handler,
        )

        return asgi_app

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
