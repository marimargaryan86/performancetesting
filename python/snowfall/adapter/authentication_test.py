import datetime
from unittest import mock

import grpc
import pytest
from google.protobuf import struct_pb2

from snowfall.adapter import authentication
from snowfall.service.authentication.v1 import (
    models_pb2,
    sessions_pb2,
    sessions_pb2_grpc,
)
from snowfall.stdlib import authentication as stdlib_auth


@pytest.fixture()
def factory() -> authentication.JWTFactory:
    return authentication.JWTFactory(ttl=datetime.timedelta(hours=1))


@pytest.fixture()
def user() -> models_pb2.User:
    return models_pb2.User()


def test_expiry(factory: authentication.JWTFactory, user: models_pb2.User) -> None:
    payload = factory.from_user(user)

    assert payload.exp


def test_version(factory: authentication.JWTFactory, user: models_pb2.User) -> None:
    payload = factory.from_user(user)

    assert payload.version >= "2.0.0"


def error_stub() -> sessions_pb2_grpc.SessionServiceStub:
    error = grpc.aio.AioRpcError(
        code=grpc.StatusCode.NOT_FOUND,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )
    stub = mock.create_autospec(sessions_pb2_grpc.SessionServiceStub)
    stub.GetSession = mock.AsyncMock(side_effect=error)

    return stub


def inactive_stub() -> sessions_pb2_grpc.SessionServiceStub:
    response = sessions_pb2.GetSessionResponse(
        session=sessions_pb2.Session(),
    )
    stub = mock.create_autospec(sessions_pb2_grpc.SessionServiceStub)
    stub.GetSession = mock.AsyncMock(return_value=response)

    return stub


def basic_stub() -> sessions_pb2_grpc.SessionServiceStub:
    response = sessions_pb2.GetSessionResponse(
        session=sessions_pb2.Session(
            active=True,
            identity=sessions_pb2.Session.Identity(
                id="bar",
                email="foo@bar.com",
            ),
        ),
    )
    stub = mock.create_autospec(sessions_pb2_grpc.SessionServiceStub)
    stub.GetSession = mock.AsyncMock(return_value=response)

    return stub


def metadata_stub() -> sessions_pb2_grpc.SessionServiceStub:
    some_struct = struct_pb2.Struct()
    some_struct.update({"foo": "bar"})
    response = sessions_pb2.GetSessionResponse(
        session=sessions_pb2.Session(
            active=True,
            identity=sessions_pb2.Session.Identity(
                id="bar",
                email="foo@bar.com",
                metadata_public=some_struct,
            ),
        ),
    )
    stub = mock.create_autospec(sessions_pb2_grpc.SessionServiceStub)
    stub.GetSession = mock.AsyncMock(return_value=response)

    return stub


class TestSessionCookieResolver(object):
    async def test_grpc_error_raises_error(self) -> None:
        resolver = authentication.session_cookie_resolver(error_stub())

        with pytest.raises(stdlib_auth.AuthenticationError):
            await resolver("foo")

    async def test_inactive_session_raises_error(self) -> None:
        resolver = authentication.session_cookie_resolver(inactive_stub())

        with pytest.raises(stdlib_auth.AuthenticationError):
            await resolver("foo")

    async def test_user_identity_is_set(self) -> None:
        resolver = authentication.session_cookie_resolver(basic_stub())
        user_response = await resolver("foo")
        assert user_response.identifier

    async def test_user_email_is_set(self) -> None:
        resolver = authentication.session_cookie_resolver(basic_stub())
        user_response = await resolver("foo")
        assert user_response.email

    async def test_user_metadata_is_empty(self) -> None:
        resolver = authentication.session_cookie_resolver(basic_stub())
        user_response = await resolver("foo")
        assert not user_response.metadata

    async def test_user_metadata_is_set(self) -> None:
        resolver = authentication.session_cookie_resolver(metadata_stub())
        user_response = await resolver("foo")
        assert user_response.metadata["foo"] == "bar"
