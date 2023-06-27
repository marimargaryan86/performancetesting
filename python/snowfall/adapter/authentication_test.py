import datetime

import pytest

from snowfall.adapter import authentication
from snowfall.service.authentication.v1alpha import models_pb2


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
