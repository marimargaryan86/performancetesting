import datetime

import pytest

from snowfall.service.authentication import auth
from snowfall.service.authentication.v1alpha import models_pb2


@pytest.fixture()
def factory() -> auth.JWTFactory:
    return auth.JWTFactory(ttl=datetime.timedelta(hours=1))


@pytest.fixture()
def user() -> models_pb2.User:
    return models_pb2.User()


def test_expiry(factory: auth.JWTFactory, user: models_pb2.User) -> None:
    payload = factory.from_user(user)

    assert payload.exp


def test_version(factory: auth.JWTFactory, user: models_pb2.User) -> None:
    payload = factory.from_user(user)

    assert payload.version >= "2.0.0"
