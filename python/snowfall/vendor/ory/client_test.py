import datetime
import json
from collections.abc import Mapping
from typing import Any

import freezegun
import httpx
import pytest
import pytest_httpx

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.ory import client, models


def _load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.ory.client",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    with open(file_path) as file_handle:
        return json.load(file_handle)


@pytest.fixture()
def session_response() -> dict[str, Any]:
    return _load_json_fixture("sessions_whoami")


@pytest.fixture()
def session_model(session_response: Mapping[str, Any]) -> models.Session:
    return models.Session(**session_response)


@pytest.fixture()
def identity_model(session_response: Mapping[str, Any]) -> models.Identity:
    return models.Session(**session_response).identity


@pytest.fixture()
def ory_client() -> client.OryClient:
    return client.OryClient(
        base_url="https://test_url",
    )


class TestClient(object):
    async def test_get_session_with_invalid_cookie(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        ory_client: client.OryClient,
    ) -> None:
        httpx_mock.add_response(
            status_code=401,
            json=_load_json_fixture("sessions_whoami_401"),
        )

        with pytest.raises(httpx.HTTPStatusError):
            await ory_client.get_session(cookie="invalid")

    async def test_get_session_with_valid_cookie(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        ory_client: client.OryClient,
        session_response: Mapping[str, Any],
    ) -> None:
        httpx_mock.add_response(json=session_response)
        session = await ory_client.get_session(cookie="valid")

        assert session.active


class TestSessionModel(object):
    def test_session_has_identifier(self, session_model: models.Session) -> None:
        assert session_model.identifier

    def test_session_is_active(self, session_model: models.Session) -> None:
        assert session_model.active

    @freezegun.freeze_time("2023-07-05 12:00:00Z")
    def test_session_has_expiry(self, session_model: models.Session) -> None:
        assert session_model.expires_at > datetime.datetime.now(datetime.UTC)

    def test_identity_has_identifier(self, identity_model: models.Identity) -> None:
        assert identity_model.identifier

    def test_identity_has_email_trait(self, identity_model: models.Identity) -> None:
        assert identity_model.traits.email
