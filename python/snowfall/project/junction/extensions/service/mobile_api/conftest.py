import copy
import dataclasses
import datetime
import pathlib
import re
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from functools import partial
from typing import Any, TypedDict
from unittest import mock

import aiofiles
import aiosmtplib
import httpx
import lagom
import mongomock_motor
import orjson
import pytest
from bson import json_util
from fakeredis import aioredis as fakeredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.extensions.service.mobile_api import (
    bootstrap,
    jwt_generator,
    middleware,
    repository,
    smtp,
    spec,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    plus_client as plus_poc_http_client,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import router
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.plus.adapter import flight_delay_predictor, trip_info
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    models_pb2 as plus_services_models_pb2,
)
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import bills, credit_card_payment
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1 import phone_number_pb2
from snowfall.vendor.junction import client as base_client
from snowfall.vendor.junction.go import client
from snowfall.vendor.junction.plus import client as plus_http_client

_FIXTURES_PATH = (
    "python/snowfall/project/junction/extensions/service/mobile_api/fixtures/{path}"
)
_RESPONSE_FIXTURES_PATH = "python/snowfall/project/junction/extensions/service/mobile_api/fixtures/junction_responses/{path}"

jwt_token_version = "1.0.0"
jwt_payload = {"version": jwt_token_version, "client_id": "test"}
junction_api_address = "https://api.junction.dev"
plus_api_address = "https://plus.junction.dev"


@pytest.fixture()
def new_user() -> models_pb2.User:
    return models_pb2.User(
        id=string.uuid(),
        email="new_user@gmail.com",
        password="ReallyString1!",
        phone=phone_number_pb2.PhoneNumber(e164_number="+306966661752"),
        first_name="New",
        last_name="User",
    )


class ExistingUser(TypedDict):
    model: models_pb2.User
    unhashed_password: str


@pytest.fixture()
def existing_user() -> ExistingUser:
    user = models_pb2.User(
        id=string.uuid(),
        email="existing_user@gmail.com",
        password="$2a$12$bb8.n1wWBXhUdJUToN.qoebWG2aZb7bMJD820mfcMDt2MW5e21VaK",
        first_name="Existing",
        last_name="User",
        phone=phone_number_pb2.PhoneNumber(e164_number="+306966661752"),
    )
    return {"model": user, "unhashed_password": "ReallyStrong1!"}


@pytest.fixture()
def existing_guest() -> models_pb2.Guest:
    return models_pb2.Guest(
        id=string.uuid(),
    )


@dataclasses.dataclass(frozen=True)
class VerificationCode:
    email: str
    code: str


@pytest.fixture()
def new_user_verification_code(new_user: models_pb2.User) -> VerificationCode:
    return VerificationCode(new_user.email, "1277")


@pytest.fixture()
def existing_user_verification_code(existing_user: ExistingUser) -> VerificationCode:
    return VerificationCode(existing_user["model"].email, "1337")


async def load_bson_fixture(path: str, base_path: str = _FIXTURES_PATH) -> Any:
    async with aiofiles.open(base_path.format(path=path)) as json_file:
        return json_util.loads(await json_file.read())


async def load_json_fixture(path: str, base_path: str = _FIXTURES_PATH) -> Any:
    async with aiofiles.open(base_path.format(path=path)) as json_file:
        return orjson.loads(await json_file.read())


class Response(TypedDict):
    url: re.Pattern[str]
    method: str
    status_code: int
    json: dict[str, Any]


async def load_response_fixture(path: str) -> Response:
    response_dict = await load_json_fixture(path, _RESPONSE_FIXTURES_PATH)
    response_dict["url"] = re.compile(
        ".*{path_regex}".format(path_regex=response_dict["url"]),
    )
    return response_dict


def get_bill(bill_id: str) -> transactions_models_pb2.Bill:
    money_usd = money.from_string("1000", money.Currency("USD")).protobuf()
    return transactions_models_pb2.Bill(
        id=bill_id,
        order_id=string.uuid(),
        is_reconciled=False,
        total_amount=money_usd,
    )


@pytest.fixture()
async def places_fixture() -> Sequence[dict[str, Any]]:
    return await load_bson_fixture("places.bson")


@pytest.fixture()
def mongo_test_db() -> mongomock_motor.AsyncMongoMockDatabase:
    return mongomock_motor.AsyncMongoMockClient()["tests"]


def _create_app(
    dependencies: lagom.Container,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_routes(dependencies),
    )
    asgi_app.add_exception_handler(
        httpx.HTTPStatusError,
        partial(
            mobile_handlers.go_status_error_handler,
            go_urls=["https://api.junction.dev"],
        ),
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    return asgi_app


@pytest.fixture()
def redis_client(decoding_redis_client: fakeredis.FakeRedis) -> redis.Client[str]:
    return redis.Client(
        decoding_redis_client,
        prefix="mobile-api",
    )


@pytest.fixture()
def smtp_client() -> smtp.EmailClient:
    smtp_client = smtp.EmailClient(aiosmtplib.SMTP(), "client", "support@example.com")
    smtp_client.send_email_html_template = mock.AsyncMock()  # type: ignore[method-assign]
    return smtp_client


@pytest.fixture()
async def notification_tokens_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.NotificationTokensRepository:
    return repository.NotificationTokensRepository(
        mongo_test_db["notifications"],
    )


@pytest.fixture()
async def preferences_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.PreferencesRepository:
    return repository.PreferencesRepository(
        mongo_test_db["preferences"],
    )


@pytest.fixture()
async def vouchers_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.VouchersRepository:
    return repository.VouchersRepository(
        mongo_test_db["vouchers"],
    )


@pytest.fixture()
async def loyalty_programs_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.LoyaltyProgramsRepository:
    return repository.LoyaltyProgramsRepository(
        mongo_test_db["air_loyalty"],
    )


@pytest.fixture()
async def orders_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.OrdersRepository:
    return repository.OrdersRepository(
        mongo_test_db["orders"],
    )


@pytest.fixture()
async def user_groups_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.UserGroupsRepository:
    return repository.UserGroupsRepository(
        mongo_test_db["user_groups"],
    )


@pytest.fixture()
async def users_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
    existing_user: ExistingUser,
) -> repository.UsersRepository:
    users_repo = repository.UsersRepository(
        mongo_test_db["users"],
    )
    await users_repo.insert(
        existing_user["model"],
    )
    return users_repo


@pytest.fixture()
async def guests_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
    existing_guest: models_pb2.Guest,
) -> repository.GuestsRepository:
    guests_repo = repository.GuestsRepository(
        mongo_test_db["guests"],
    )
    await guests_repo.insert(existing_guest)
    return guests_repo


@pytest.fixture()
async def otp_repository(
    redis_client: redis.Client[str],
    new_user_verification_code: VerificationCode,
    existing_user_verification_code: VerificationCode,
) -> repository.OtpRepository:
    otp_repo = repository.OtpRepository(redis_client, datetime.timedelta(minutes=10))
    await otp_repo.create(
        new_user_verification_code.email,
        new_user_verification_code.code,
    )
    await otp_repo.create(
        existing_user_verification_code.email,
        existing_user_verification_code.code,
    )
    return otp_repo


@pytest.fixture()
async def enums_values_repository(
    redis_client: redis.Client[str],
) -> repository.EnumsValuesRepository:
    return repository.EnumsValuesRepository(
        redis_client,
    )


@pytest.fixture()
async def places_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
    places_fixture: Sequence[Mapping[str, Any]],
) -> repository.PlacesRepository:
    places_repo = repository.PlacesRepository(
        mongo_test_db["places"],
    )
    await places_repo._collection.insert_many(places_fixture)  # noqa: SLF001
    return places_repo


@pytest.fixture()
async def markups_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.MarkupsRepository:
    return repository.MarkupsRepository(
        mongo_test_db["markups"],
    )


@pytest.fixture()
def jwt_gen() -> jwt_generator.JwtGenerator:
    return jwt_generator.JwtGenerator(
        encoder=jwt.Encoder(),
        token_version=jwt_token_version,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }


@pytest.fixture()
def junction_client() -> client.Client:
    return client.Client(base_url=junction_api_address)


@pytest.fixture()
def bills_client() -> bills.Client:
    return bills.DictClient(
        [get_bill(bill_id) for bill_id in pay_fixtures.BILLS],
    )


@pytest.fixture()
def predictions_client() -> flight_delay_predictor.Client:
    return flight_delay_predictor.DictClient(
        predictions=[
            flight_delay_predictor.Prediction(
                id="AA1002023-10-30T00:00:01Z",
                flight_number="AA100",
                scheduled_departure_at="2023-10-30T00:00:01Z",
                delay=13.79,  # noqa: WPS432
            ),
            flight_delay_predictor.Prediction(
                id="AA2002023-10-30T00:00:01Z",
                flight_number="AA200",
                scheduled_departure_at="2023-11-01T00:00:01Z",
                delay=-12.75,  # noqa: WPS432
            ),
        ],
    )


@pytest.fixture()
def credit_card_payment_client() -> credit_card_payment.Client:
    return credit_card_payment.DictClient()


@pytest.fixture()
def trip_info_client() -> trip_info.Client:
    return trip_info.DictClient(
        emissions=[
            plus_services_models_pb2.FlightEmission(
                origin="LHR",
                destination="ATH",
                flight_number=100,
                operating_carrier_code="AA",
            ),
        ],
        flight_statuses=[
            plus_services_models_pb2.FlightStatus(
                flight_id=1226913573,
                carrier_fs_code="AA",
                flight_number="100",
                status="L",
                airport_resources=plus_services_models_pb2.AirportResources(
                    departure_terminal="8",
                    departure_gate="12",
                    arrival_terminal="3",
                    arrival_gate="31",
                    baggage="10",
                ),
            ),
        ],
        visa_requirements=[
            plus_services_models_pb2.ServiceIntent(
                redirect_uri="https://travel.fluxir.com/applications/external?serviceIntentKey=Visa-Fluxir-ARE-2&from=01-01-2024&to=01-02-2024&origination=JOR&destination=ARE&tokenStoreKey=9910f620-1b29-4136-8e54-14bb82b1ae45",
                title="United Arab Emirates (the) Tourist one month",
                description="Single entry - 3 days processing time - Validity 2 Months",
                info="A one month tourist visa for the United Arab Emirates allows an individual to visit the UAE for a period of up to 30 days. This type of visa is typically issued for single entry, meaning that the holder can only enter the UAE once during the validity of the visa. The purpose of the visit must be tourism or business, and the visa holder is not allowed to work or engage in any other activities that are not related to tourism or business.",
                fee=96,
                approval_rate="123",
                appliers_count="98",
                expected_processing_time="30",
                stay_duration="30",
                validity_period="2",
                stay_duration_unit="Days",
                validity_period_unit="Months",
            ),
        ],
    )


@pytest.fixture()
def plus_client() -> plus_http_client.Client:
    return plus_http_client.Client(base_url=junction_api_address)


@pytest.fixture()
def plus_poc_client() -> plus_poc_http_client.PlusClient:
    return plus_poc_http_client.PlusClient(
        api_url=plus_api_address,
        activated=True,
    )


@pytest.fixture()
def non_mocked_hosts() -> list[str]:
    return ["example.com"]


@pytest.fixture()
def app(
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    guests_repository: repository.GuestsRepository,
    otp_repository: repository.OtpRepository,
    enums_values_repository: repository.EnumsValuesRepository,
    smtp_client: smtp.EmailClient,
    orders_repository: repository.OrdersRepository,
    junction_client: client.Client,
    plus_client: plus_http_client.Client,
    plus_poc_client: plus_poc_http_client.PlusClient,
    jwt_gen: jwt_generator.JwtGenerator,
    loyalty_programs_repository: repository.LoyaltyProgramsRepository,
    preferences_repository: repository.PreferencesRepository,
    vouchers_repository: repository.VouchersRepository,
    notification_tokens_repository: repository.NotificationTokensRepository,
    user_groups_repository: repository.UserGroupsRepository,
    markups_repository: repository.MarkupsRepository,
    bills_client: bills.Client,
    predictions_client: flight_delay_predictor.Client,
    trip_info_client: trip_info.Client,
    credit_card_payment_client: credit_card_payment.Client,
) -> Iterator[applications.Starlette]:
    with spec.get_api_spec() as temp_spec_path:
        yield _create_app(
            dependencies=bootstrap.create_dependencies(
                orders_repository,
                junction_client,
                plus_client,
                base_client.create_httpx_client(base_url=junction_api_address),
                plus_poc_client,
                places_repository,
                users_repository,
                guests_repository,
                otp_repository,
                enums_values_repository,
                smtp_client,
                jwt_gen,
                bootstrap.Switcher(create_stripe_customers=True),
                loyalty_programs_repository,
                preferences_repository,
                vouchers_repository,
                notification_tokens_repository,
                user_groups_repository,
                markups_repository,
                bills_client,
                predictions_client,
                trip_info_client,
                credit_card_payment_client,
            ),
            openapi_path=temp_spec_path,
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=middleware.AuthenticationBackend(
                        decoder=jwt.Decoder(),
                        token_version=jwt_token_version,
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
        )


@pytest.fixture()
async def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
async def authenticated_http_client(
    app: applications.Starlette,
    jwt_gen: jwt_generator.JwtGenerator,
    existing_user: ExistingUser,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    new_headers = dict(copy.copy(headers))

    new_headers["Authorization"] = "Bearer {token}".format(
        token=jwt_gen.encode(existing_user["model"].id),
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(new_headers))

        yield client
