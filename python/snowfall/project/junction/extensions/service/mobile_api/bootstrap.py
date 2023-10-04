import datetime
from collections.abc import Sequence

import httpx
import lagom
from pydantic import AnyUrl, HttpUrl

from snowfall.project.junction.extensions.service.mobile_api import (
    jwt_generator,
    plus_client,
    repository,
    smtp,
)
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.junction.go import client


class MigrateSettings(application.Settings):
    mongo_db: str
    mongo_dsn: AnyUrl


class Settings(application.Settings):
    junction_api_address: str
    ory_client_token_endpoint: HttpUrl
    ory_client_id: str
    ory_client_secret: str
    plus_api_address: str = ""
    plus_activated: bool = False
    redis_dsn: Sequence[AnyUrl]
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    otp_cache_ttl: datetime.timedelta = datetime.timedelta(minutes=2)
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
    cookie_auth_enabled: bool = False
    authentication_address: str | None = None
    junction_private_key: str | None = None


def create_dependencies(  # noqa: WPS211
    orders_repository: repository.OrdersRepository,
    junction_client: client.Client,
    httpx_client: httpx.AsyncClient,
    plus_http_client: plus_client.PlusClient,
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    guests_repository: repository.GuestsRepository,
    otp_repository: repository.OtpRepository,
    enums_values_repository: repository.EnumsValuesRepository,
    smtp_client: smtp.EmailClient,
    jwt_gen: jwt_generator.JwtGenerator,
    stripe_users_repository: repository.StripeUsersRepository,
    loyalty_programs_repository: repository.LoyaltyProgramsRepository,
    preferences_repository: repository.PreferencesRepository,
    vouchers_repository: repository.VouchersRepository,
    notification_tokens_repository: repository.NotificationTokensRepository,
    user_groups_repository: repository.UserGroupsRepository,
    markups_repository: repository.MarkupsRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[repository.OrdersRepository] = orders_repository
    container[client.Client] = junction_client
    container[httpx.AsyncClient] = httpx_client
    container[plus_client.PlusClient] = plus_http_client
    container[repository.PlacesRepository] = places_repository
    container[repository.UsersRepository] = users_repository
    container[repository.GuestsRepository] = guests_repository
    container[repository.OtpRepository] = otp_repository
    container[repository.EnumsValuesRepository] = enums_values_repository
    container[smtp.EmailClient] = smtp_client
    container[jwt_generator.JwtGenerator] = jwt_gen
    container[repository.StripeUsersRepository] = stripe_users_repository
    container[repository.LoyaltyProgramsRepository] = loyalty_programs_repository
    container[repository.PreferencesRepository] = preferences_repository
    container[repository.VouchersRepository] = vouchers_repository
    container[repository.NotificationTokensRepository] = notification_tokens_repository
    container[repository.UserGroupsRepository] = user_groups_repository
    container[repository.MarkupsRepository] = markups_repository
    return container
