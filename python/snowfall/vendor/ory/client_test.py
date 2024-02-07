import datetime
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

import aiofiles
import freezegun
import httpx
import orjson
import pytest
import pytest_httpx

from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.vendor.ory import client, models

UPDATED_METADATA_PUBLIC = MappingProxyType(
    {
        "role": "reseller-admin",
        "reseller_id": "some-reseller-id",
    },
)
UPDATED_EMAIL = "new@email.com"


async def _load_json_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.ory.client",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
async def mock_identity_response() -> dict[str, Any]:
    return await _load_json_fixture("mock_identity_response")


@pytest.fixture()
async def session_response() -> dict[str, Any]:
    return await _load_json_fixture("sessions_whoami")


@pytest.fixture()
def session_model(session_response: Mapping[str, Any]) -> models.Session:
    return models.Session(**session_response)


@pytest.fixture()
async def session_model_no_metadata() -> models.Session:
    response = await _load_json_fixture("sessions_whoami_no_metadata")
    return models.Session(**response)


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
            json=await _load_json_fixture("sessions_whoami_401"),
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

    async def test_create_identity(
        self,
        mock_identity_response: dict[str, Any],
        ory_client: client.OryClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(method="POST", json=mock_identity_response)

        email: str = mock_identity_response["traits"]["email"]
        metadata: dict[str, Any] = {"role": "reseller-admin"}

        identity: models.Identity = await ory_client.create_identity(email, metadata)

        assert identity.traits.email == mock_identity_response["traits"]["email"]
        assert (
            identity.metadata_public["role"]
            == mock_identity_response["metadata_public"]["role"]
        )

    async def test_update_identity(
        self,
        mock_identity_response: dict[str, Any],
        ory_client: client.OryClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(method="PATCH", json=mock_identity_response)

        identity = models.Identity(**mock_identity_response)

        updated_identity = await ory_client.update_identity(identity)

        assert updated_identity.traits.email == identity.traits.email
        assert (
            updated_identity.metadata_public["reseller_id"]
            == identity.metadata_public["reseller_id"]
        )
        assert (
            updated_identity.metadata_public["role"] == identity.metadata_public["role"]
        )

    async def test_delete_identity(
        self,
        ory_client: client.OryClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(status_code=204)
        await ory_client.delete_identity(identifier="user_id_string")
        request = httpx_mock.get_request()
        assert request
        assert request.method == "DELETE"
        assert request.url.path == "/admin/identities/user_id_string"

    async def test_list_identities(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        ory_client: client.OryClient,
    ) -> None:
        httpx_mock.add_response(json=await _load_json_fixture("identities"))

        identities = await ory_client.list_identities()

        assert len(identities.identities) == 2

    async def test_list_identities_by_ids(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        ory_client: client.OryClient,
    ) -> None:
        json = await _load_json_fixture("identities")
        next_identity = next(iter(json))
        ids = [next_identity["id"]]

        httpx_mock.add_response(json=[next_identity])

        identities = await ory_client.list_identities(ids=ids)

        assert len(identities.identities) == 1
        for identity in identities.identities:
            assert identity.identifier in ids

    async def test_list_identities_paginated(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        ory_client: client.OryClient,
    ) -> None:
        json = await _load_json_fixture("identities")
        httpx_mock.add_response(
            json=[next(iter(json))],
            headers={
                "link": '</admin/identities?page_size=10&page_token=00000000-0000-0000-0000-000000000000>; rel="first",</admin/identities?page_size=10&page_token=2adf410f-8fe1-43db-9fce-e1dab46f224e>; rel="next"',
            },
        )

        identities = await ory_client.list_identities(page_size=1)

        assert len(identities.identities) == 1
        assert identities.next_page_token

        httpx_mock.add_response(
            json=[next(iter(json))],
            headers={
                "link": '</admin/identities?page_size=50&page_token=00000000-0000-0000-0000-000000000000>; rel="first"',
            },
        )

        page_token = cursor.marshal(identities.next_page_token)
        identities = await ory_client.list_identities(
            page_size=1,
            page_token=cursor.unmarshal(page_token).id,
        )

        assert len(identities.identities) == 1
        assert not identities.next_page_token


class TestSessionModel(object):
    def test_session_has_identifier(self, session_model: models.Session) -> None:
        assert session_model.identifier

    def test_session_is_active(self, session_model: models.Session) -> None:
        assert session_model.active

    def test_identity_no_metadata(
        self,
        session_model_no_metadata: models.Session,
    ) -> None:
        assert not session_model_no_metadata.identity.metadata_public

    @freezegun.freeze_time("2023-07-05 12:00:00Z")
    def test_session_has_expiry(self, session_model: models.Session) -> None:
        assert session_model.expires_at > datetime.datetime.now(datetime.UTC)

    def test_identity_has_identifier(self, identity_model: models.Identity) -> None:
        assert identity_model.identifier

    def test_identity_has_email_trait(self, identity_model: models.Identity) -> None:
        assert identity_model.traits.email

    def test_identity_has_metadata_reseller(
        self,
        identity_model: models.Identity,
    ) -> None:
        assert identity_model.metadata_public.get("reseller_id")
