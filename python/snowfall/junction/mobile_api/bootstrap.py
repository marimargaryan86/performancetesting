# flake8: noqa: WPS201
import datetime
import ipaddress
from typing import Optional, Sequence

import lagom
from lagom.integrations import starlette
from pydantic import AnyUrl
from starlette import applications, exceptions, status
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import jwt_generator, repository, smtp
from snowfall.junction.mobile_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers
from snowfall.vendor.junction import client


class Settings(service.Settings):
    junction_api_address: Sequence[str]
    junction_api_token: str
    redis_dsn: Sequence[AnyUrl]

    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    otp_cache_ttl: datetime.timedelta = datetime.timedelta(minutes=2)
    smtp_dsn: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    jwt_private_key: str
    jwt_token_version: str
    jwt_public_key: str
    stripe_api_key: str


def create_dependencies(  # noqa: WPS211
    offers_repository: repository.OffersRepository,
    orders_repository: repository.OrdersRepository,
    junction_client: client.JunctionClient,
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    otp_repository: repository.OtpRepository,
    trip_searches_repository: repository.TripSearchesRepository,
    trips_repository: repository.TripsRepository,
    smtp_client: smtp.EmailClient,
    jwt_gen: jwt_generator.JwtGenerator,
    stripe_users_repository: repository.StripeUsersRepository,
    payment_intent_repository: repository.PaymentIntentRepository,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[repository.OffersRepository] = offers_repository
    container[repository.OrdersRepository] = orders_repository
    container[client.JunctionClient] = junction_client
    container[repository.PlacesRepository] = places_repository
    container[repository.UsersRepository] = users_repository
    container[repository.OtpRepository] = otp_repository
    container[repository.TripSearchesRepository] = trip_searches_repository
    container[repository.TripsRepository] = trips_repository
    container[smtp.EmailClient] = smtp_client
    container[jwt_generator.JwtGenerator] = jwt_gen
    container[repository.StripeUsersRepository] = stripe_users_repository
    container[repository.PaymentIntentRepository] = payment_intent_repository
    return starlette.StarletteIntegration(container)


def create_app(
    dependencies: starlette.StarletteIntegration,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    app = applications.Starlette(
        routes=router.get_routes(dependencies),
        middleware=custom_middlewares,
    )
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app
