import datetime
from collections.abc import Sequence

import httpx
import lagom
from pydantic import AnyUrl, HttpUrl, RedisDsn

from snowfall.project.junction.extensions.service.mobile_api import (
    jwt_generator,
    repository,
    smtp,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    plus_client as plus_poc_http_client,
)
from snowfall.project.junction.plus.adapter import (
    flight_delay_predictor as flight_prediction_adapter,
)
from snowfall.project.junction.plus.adapter import (
    trip_info as trip_info_adapter,
)
from snowfall.project.pay.adapter import bills
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.junction.go import client as go_http_client
from snowfall.vendor.junction.plus import client as plus_http_client


class MigrateSettings(application.Settings):
    mongo_db: str
    mongo_dsn: AnyUrl


class Settings(application.Settings):
    junction_api_address: str
    plus_api_address: str
    ory_client_token_endpoint: HttpUrl
    ory_client_id: str
    ory_client_secret: str
    plus_poc_api_address: str = ""
    plus_poc_activated: bool = False
    redis_dsn: RedisDsn
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    otp_cache_ttl: datetime.timedelta = datetime.timedelta(minutes=2)
    smtp_dsn: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    flight_prediction_address: str
    co2_emissions_address: str
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
    transactions_address: str


def create_dependencies(
    orders_repository: repository.OrdersRepository,
    junction_client: go_http_client.Client,
    plus_client: plus_http_client.Client,
    httpx_client: httpx.AsyncClient,
    plus_poc_client: plus_poc_http_client.PlusClient,
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
    bills_client: bills.Client,
    predictions_client: flight_prediction_adapter.Client,
    trip_info_client: trip_info_adapter.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[repository.OrdersRepository] = orders_repository
    container[go_http_client.Client] = junction_client
    container[plus_http_client.Client] = plus_client
    container[httpx.AsyncClient] = httpx_client
    container[plus_poc_http_client.PlusClient] = plus_poc_client
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
    container[bills.Client] = bills_client  # type: ignore[type-abstract]
    container[flight_prediction_adapter.Client] = predictions_client  # type: ignore[type-abstract]
    container[trip_info_adapter.Client] = trip_info_client  # type: ignore[type-abstract]
    return container
