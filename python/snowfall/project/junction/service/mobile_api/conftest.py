import base64
import copy
import dataclasses
import datetime
import pathlib
import re
import uuid
from typing import Any, Mapping, Optional, Sequence
from unittest import mock

import aiosmtplib
import jwt as jwtlib
import mongomock_motor
import pytest
from bson import json_util
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fakeredis import aioredis as fakeredis
from lagom.integrations import starlette
from starlette import applications, testclient
from starlette.middleware import Middleware, authentication
from typing_extensions import TypedDict

from snowfall.project.junction.service.mobile_api import (
    auth_middleware,
    bootstrap,
    jwt_generator,
    repository,
    smtp,
)
from snowfall.project.junction.service.mobile_api.routes import router
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1alpha import phone_number_pb2
from snowfall.vendor.junction import client

_FIXTURES_PATH = "python/snowfall/project/junction/service/mobile_api/fixtures/{path}"
_RESPONSE_FIXTURES_PATH = "python/snowfall/project/junction/service/mobile_api/fixtures/junction_responses/{path}"  # noqa: B950

jwt_token_version = "1.0.0"  # nosec
jwt_payload = {"version": jwt_token_version, "client_id": "test"}
public_exponent = 65537
key_size = 2048
jwt_private_key = rsa.generate_private_key(
    public_exponent=public_exponent,
    key_size=key_size,
)

jwt_token = jwtlib.encode(
    payload=jwt_payload,
    key=jwt_private_key,  # type: ignore[arg-type]
    algorithm="RS256",
)
jwt_public_key_bytes = jwt_private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
jwt_public_key = base64.b64encode(jwt_public_key_bytes).decode()


@pytest.fixture
def new_user() -> models_pb2.User:
    return models_pb2.User(  # nosec
        id=str(uuid.uuid4()),
        email="new_user@gmail.com",
        password="ReallyString1!",
        phone=phone_number_pb2.PhoneNumber(e164_number="+306966661752"),
        name="New User",
    )


ExistingUser = TypedDict(
    "ExistingUser",
    {"model": models_pb2.User, "unhashed_password": str},
)


@pytest.fixture
def existing_user() -> ExistingUser:
    user = models_pb2.User(  # nosec
        id=str(uuid.uuid4()),
        email="existing_user@gmail.com",
        password="$2a$12$bb8.n1wWBXhUdJUToN.qoebWG2aZb7bMJD820mfcMDt2MW5e21VaK",
        name="Existing User",
        phone=phone_number_pb2.PhoneNumber(e164_number="+306966661752"),
    )
    return {"model": user, "unhashed_password": "ReallyStrong1!"}


@dataclasses.dataclass(frozen=True)
class VerificationCode(object):
    email: str
    code: str


@pytest.fixture
def new_user_verification_code(new_user: models_pb2.User) -> VerificationCode:
    return VerificationCode(new_user.email, "1277")


@pytest.fixture
def existing_user_verification_code(existing_user: ExistingUser) -> VerificationCode:
    return VerificationCode(existing_user["model"].email, "1337")


def load_json_fixture(path: str, base_path: str = _FIXTURES_PATH) -> Any:
    with open(base_path.format(path=path)) as json_file:
        return json_util.loads(json_file.read())


Response = TypedDict(
    "Response",
    {
        "url": re.Pattern[str],
        "method": str,
        "status_code": int,
        "json": dict[str, Any],
    },
)


def load_response_fixture(path: str) -> Response:
    response_dict = load_json_fixture(path, _RESPONSE_FIXTURES_PATH)
    response_dict["url"] = re.compile(
        r".*{path_regex}".format(path_regex=response_dict["url"]),  # noqa: WPS360
    )
    return response_dict


@pytest.fixture
def places_fixture() -> Sequence[dict[str, Any]]:
    return load_json_fixture("places.json")


@pytest.fixture
def mongo_test_db() -> mongomock_motor.AsyncMongoMockDatabase:
    return mongomock_motor.AsyncMongoMockClient()["tests"]


def _create_app(
    dependencies: starlette.StarletteIntegration,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        dependencies=dependencies,
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes_factory=router.get_routes,
    )


@pytest.fixture
def redis_client(decoding_redis_client: fakeredis.FakeRedis) -> redis.Client[str]:
    return redis.Client[str](
        decoding_redis_client,
        prefix="mobile-api",
    )


@pytest.fixture
def smtp_client() -> smtp.EmailClient:
    smtp_client = smtp.EmailClient(aiosmtplib.SMTP())
    smtp_client.send_email_notification = mock.AsyncMock()  # type: ignore[assignment]
    return smtp_client


@pytest.fixture
def offers_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.OffersRepository:
    return repository.OffersRepository(
        mongo_test_db["offers"],
    )


@pytest.fixture
def trip_searches_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.TripSearchesRepository:
    return repository.TripSearchesRepository(
        mongo_test_db["trip-searches"],
    )


@pytest.fixture
def trips_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.TripsRepository:
    return repository.TripsRepository(
        mongo_test_db["trips"],
    )


@pytest.fixture
def orders_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.OrdersRepository:
    return repository.OrdersRepository(
        mongo_test_db["orders"],
    )


@pytest.fixture
def stripe_users_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
) -> repository.StripeUsersRepository:
    return repository.StripeUsersRepository(
        mongo_test_db["stripe_users"],
    )


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
async def places_repository(
    mongo_test_db: mongomock_motor.AsyncMongoMockDatabase,
    places_fixture: Sequence[Mapping[str, Any]],
) -> repository.PlacesRepository:
    places_repo = repository.PlacesRepository(
        mongo_test_db["places"],
    )
    await places_repo._collection.insert_many(places_fixture)  # noqa: WPS437
    return places_repo


@pytest.fixture
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
def junction_client() -> client.JunctionClient:
    junction_api_address = "https://api.junction.dev"
    return client.JunctionClient(  # nosec
        api_url=junction_api_address,
        token="",
    )


@pytest.fixture()
def app(  # noqa: WPS211
    offers_repository: repository.OffersRepository,
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    otp_repository: repository.OtpRepository,
    smtp_client: smtp.EmailClient,
    orders_repository: repository.OrdersRepository,
    trip_searches_repository: repository.TripSearchesRepository,
    trips_repository: repository.TripsRepository,
    junction_client: client.JunctionClient,
    jwt_gen: jwt_generator.JwtGenerator,
    stripe_users_repository: repository.StripeUsersRepository,
) -> applications.Starlette:
    return _create_app(
        dependencies=bootstrap.create_dependencies(
            offers_repository,
            orders_repository,
            junction_client,
            places_repository,
            users_repository,
            otp_repository,
            trip_searches_repository,
            trips_repository,
            smtp_client,
            jwt_gen,
            stripe_users_repository,
        ),
        openapi_path=filesystem.resource_path("junction.mobile_api", "openapi.json"),
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=auth_middleware.AuthenticationBackend(
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
def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    http_client = testclient.TestClient(app)
    http_client.headers.update(headers)

    return http_client


@pytest.fixture()
def authenticated_http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
    jwt_gen: jwt_generator.JwtGenerator,
    existing_user: ExistingUser,
) -> testclient.TestClient:
    http_client = testclient.TestClient(app)
    authenticated_headers = dict(copy.deepcopy(headers))
    authenticated_headers["Authorization"] = "Bearer {token}".format(
        token=jwt_gen.encode(existing_user["model"].id),
    )
    http_client.headers.update(authenticated_headers)

    return http_client
