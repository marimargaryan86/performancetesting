import base64
import copy
import dataclasses
import datetime
import pathlib
import re
from collections.abc import AsyncIterator, Mapping, Sequence
from functools import partial
from typing import Any, TypedDict
from unittest import mock

import aiosmtplib
import httpx
import jwt as jwtlib
import lagom
import mongomock_motor
import pytest
from bson import json_util
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fakeredis import aioredis as fakeredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.extensions.service.mobile_api import (
    bootstrap,
    jwt_generator,
    main,
    middleware,
    plus_client,
    repository,
    smtp,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import router
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1 import phone_number_pb2
from snowfall.vendor.junction.go import client

_FIXTURES_PATH = (
    "python/snowfall/project/junction/extensions/service/mobile_api/fixtures/{path}"
)
_RESPONSE_FIXTURES_PATH = "python/snowfall/project/junction/extensions/service/mobile_api/fixtures/junction_responses/{path}"

jwt_token_version = "1.0.0"
jwt_payload = {"version": jwt_token_version, "client_id": "test"}
public_exponent = 65537
key_size = 2048
jwt_private_key = rsa.generate_private_key(
    public_exponent=public_exponent,
    key_size=key_size,
)

jwt_token = jwtlib.encode(
    payload=jwt_payload,
    key=jwt_private_key,
    algorithm="RS256",
)
jwt_public_key_bytes = jwt_private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
jwt_public_key = base64.b64encode(jwt_public_key_bytes).decode()
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
class VerificationCode(object):
    email: str
    code: str


@pytest.fixture()
def new_user_verification_code(new_user: models_pb2.User) -> VerificationCode:
    return VerificationCode(new_user.email, "1277")


@pytest.fixture()
def existing_user_verification_code(existing_user: ExistingUser) -> VerificationCode:
    return VerificationCode(existing_user["model"].email, "1337")


def load_json_fixture(path: str, base_path: str = _FIXTURES_PATH) -> Any:
    with open(base_path.format(path=path)) as json_file:
        return json_util.loads(json_file.read())


class Response(TypedDict):
    url: re.Pattern[str]
    method: str
    status_code: int
    json: dict[str, Any]


def load_response_fixture(path: str) -> Response:
    response_dict = load_json_fixture(path, _RESPONSE_FIXTURES_PATH)
    response_dict["url"] = re.compile(
        ".*{path_regex}".format(path_regex=response_dict["url"]),
    )
    return response_dict


@pytest.fixture()
def places_fixture() -> Sequence[dict[str, Any]]:
    return load_json_fixture("places.json")


@pytest.fixture()
def mongo_test_db() -> mongomock_motor.AsyncMongoMockDatabase:
    return mongomock_motor.AsyncMongoMockClient()["tests"]


def _create_app(
    dependencies: lagom.Container,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    client_api_spec_path = str(
        filesystem.resource_path(
            "junction.client_api",
            "openapi.json",
        ),
    )
    main.replace_in_file(
        client_api_spec_path,
        '"$ref": "#/',
        '"$ref": "./../client_api/openapi.json#/',
    )
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
def notification_tokens_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.NotificationTokensRepository:
    return repository.NotificationTokensRepository(
        mongo_test_db["notifications"],
    )


@pytest.fixture()
def preferences_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.PreferencesRepository:
    return repository.PreferencesRepository(
        mongo_test_db["preferences"],
    )


@pytest.fixture()
def vouchers_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.VouchersRepository:
    return repository.VouchersRepository(
        mongo_test_db["vouchers"],
    )


@pytest.fixture()
def loyalty_programs_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.LoyaltyProgramsRepository:
    return repository.LoyaltyProgramsRepository(
        mongo_test_db["air_loyalty"],
    )


@pytest.fixture()
def orders_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.OrdersRepository:
    return repository.OrdersRepository(
        mongo_test_db["orders"],
    )


@pytest.fixture()
def user_groups_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.UserGroupsRepository:
    return repository.UserGroupsRepository(
        mongo_test_db["user_groups"],
    )


@pytest.fixture()
def stripe_users_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.StripeUsersRepository:
    return repository.StripeUsersRepository(
        mongo_test_db["stripe_users"],
        create_stripe_customers=True,
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
    await places_repo._collection.insert_many(places_fixture)  # noqa: WPS437
    return places_repo


@pytest.fixture()
def jwt_gen() -> jwt_generator.JwtGenerator:
    return jwt_generator.JwtGenerator(
        base64.b64encode(
            jwt_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ),
        ).decode(),
        jwt_token_version,
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
def plus_http_client() -> plus_client.PlusClient:
    return plus_client.PlusClient(
        api_url=plus_api_address,
        activated=True,
    )


@pytest.fixture()
def non_mocked_hosts() -> list[str]:
    return ["example.com"]


@pytest.fixture()
def app(  # noqa: WPS211
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    guests_repository: repository.GuestsRepository,
    otp_repository: repository.OtpRepository,
    enums_values_repository: repository.EnumsValuesRepository,
    smtp_client: smtp.EmailClient,
    orders_repository: repository.OrdersRepository,
    junction_client: client.Client,
    plus_http_client: plus_client.PlusClient,
    jwt_gen: jwt_generator.JwtGenerator,
    stripe_users_repository: repository.StripeUsersRepository,
    loyalty_programs_repository: repository.LoyaltyProgramsRepository,
    preferences_repository: repository.PreferencesRepository,
    vouchers_repository: repository.VouchersRepository,
    notification_tokens_repository: repository.NotificationTokensRepository,
    user_groups_repository: repository.UserGroupsRepository,
) -> applications.Starlette:
    return _create_app(
        dependencies=bootstrap.create_dependencies(
            orders_repository,
            junction_client,
            plus_http_client,
            places_repository,
            users_repository,
            guests_repository,
            otp_repository,
            enums_values_repository,
            smtp_client,
            jwt_gen,
            stripe_users_repository,
            loyalty_programs_repository,
            preferences_repository,
            vouchers_repository,
            notification_tokens_repository,
            user_groups_repository,
        ),
        openapi_path=filesystem.resource_path("junction.mobile_api", "openapi.json"),
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=middleware.AuthenticationBackend(
                    token_version=jwt_token_version,
                    public_key=base64.b64decode(
                        jwt_public_key,
                    ).decode(),
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
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
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

    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(new_headers))

        yield client
