import datetime
from typing import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.project.junction.service.mobile_api import (
    currencies,
    jwt_generator,
    repository,
    smtp,
)
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.junction import client


class Settings(application.Settings):
    currencies_address: Sequence[str]
    junction_api_address: Sequence[str]
    junction_api_token: str
    redis_dsn: Sequence[AnyUrl]
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    otp_cache_ttl: datetime.timedelta = datetime.timedelta(minutes=2)
    offers_rates_cache_ttl: datetime.timedelta = datetime.timedelta(
        minutes=45,  # noqa: WPS432
    )
    currency_rate_cache_ttl: datetime.timedelta = datetime.timedelta(
        minutes=10,
    )
    fallback_rate_sek: float = 10.85
    smtp_dsn: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    jwt_private_key: str
    jwt_token_version: str
    jwt_public_key: str
    stripe_api_key: str
    client_name: str
    support_email: str
    create_stripe_customers: bool
    mongo_db: str
    validate_responses_against_spec: bool = True


def create_dependencies(  # noqa: WPS211
    currencies_client: currencies.CurrencyClient,
    orders_repository: repository.OrdersRepository,
    junction_client: client.JunctionClient,
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    otp_repository: repository.OtpRepository,
    offers_rates_repository: repository.OffersRatesRepository,
    smtp_client: smtp.EmailClient,
    jwt_gen: jwt_generator.JwtGenerator,
    stripe_users_repository: repository.StripeUsersRepository,
    loyalty_programs_repository: repository.LoyaltyProgramsRepository,
    preferences_repository: repository.PreferencesRepository,
    vouchers_repository: repository.VouchersRepository,
    notification_tokens_repository: repository.NotificationTokensRepository,
    user_groups_repository: repository.UserGroupsRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[currencies.CurrencyClient] = currencies_client
    container[repository.OrdersRepository] = orders_repository
    container[client.JunctionClient] = junction_client
    container[repository.PlacesRepository] = places_repository
    container[repository.UsersRepository] = users_repository
    container[repository.OtpRepository] = otp_repository
    container[repository.OffersRatesRepository] = offers_rates_repository
    container[smtp.EmailClient] = smtp_client
    container[jwt_generator.JwtGenerator] = jwt_gen
    container[repository.StripeUsersRepository] = stripe_users_repository
    container[repository.LoyaltyProgramsRepository] = loyalty_programs_repository
    container[repository.PreferencesRepository] = preferences_repository
    container[repository.VouchersRepository] = vouchers_repository
    container[repository.NotificationTokensRepository] = notification_tokens_repository
    container[repository.UserGroupsRepository] = user_groups_repository
    return container
