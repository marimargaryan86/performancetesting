import dataclasses

import pytest
from starlette import authentication

from snowfall.project.junction.go.service.client_api import authentication as api_auth
from snowfall.stdlib.format import jwt


@dataclasses.dataclass(kw_only=True, frozen=True)
class _Version1Payload(jwt.Payload):
    client_id: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class _VersionedPayload(jwt.Payload):
    version: str


@pytest.fixture()
def legacy_auth() -> api_auth.LegacyAuth:
    return api_auth.LegacyAuth(
        jwt.Decoder(),
        jwt_version="1.0.0",
    )


def test_invalid_jwt_raises_error(legacy_auth: api_auth.LegacyAuth) -> None:
    with pytest.raises(authentication.AuthenticationError):
        legacy_auth.get_reseller_id_from_jwt("foo")


def test_unknown_jwt_version_raises_error(legacy_auth: api_auth.LegacyAuth) -> None:
    jwt_token = jwt.Encoder().encode(jwt.Payload())

    with pytest.raises(authentication.AuthenticationError):
        legacy_auth.get_reseller_id_from_jwt(jwt_token)


def test_missing_user_data_raises_error(legacy_auth: api_auth.LegacyAuth) -> None:
    jwt_token = jwt.Encoder().encode(_VersionedPayload(version="2.0.0"))

    with pytest.raises(authentication.AuthenticationError):
        legacy_auth.get_reseller_id_from_jwt(jwt_token)


def test_v1_jwt_resolves_reseller(
    legacy_auth: api_auth.LegacyAuth,
) -> None:
    jwt_token = jwt.Encoder().encode(_Version1Payload(client_id="foo"))
    assert legacy_auth.get_reseller_id_from_jwt(jwt_token) == "foo"


def test_v2_jwt_resolves_reseller(
    legacy_auth: api_auth.LegacyAuth,
    jwt_token: str,
) -> None:
    assert legacy_auth.get_reseller_id_from_jwt(jwt_token) == "foo"
