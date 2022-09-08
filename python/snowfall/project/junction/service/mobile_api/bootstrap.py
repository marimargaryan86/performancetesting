import datetime
from typing import Sequence

import lagom
from lagom.integrations import starlette
from pydantic import AnyUrl

from snowfall.project.junction.service.mobile_api import jwt_generator, repository, smtp
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.junction import client


class Settings(application.Settings):
    junction_api_address: Sequence[str]
    junction_api_token: str
    redis_dsn: Sequence[AnyUrl]
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
    loyalty_programs_repository: repository.LoyaltyProgramsRepository,
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
    container[repository.LoyaltyProgramsRepository] = loyalty_programs_repository
    return starlette.StarletteIntegration(container)
