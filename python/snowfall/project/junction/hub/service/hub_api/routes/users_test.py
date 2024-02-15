import copy
from collections.abc import Sequence
from typing import Any

import httpx
import pytest
from starlette import status

from snowfall.project.junction.hub.service.hub_api import conftest, repository
from snowfall.service.authentication.v1 import identities_pb2


@pytest.mark.parametrize(
    ("email", "role", "reseller_id", "expected_status", "test_id"),
    [
        (
            "john@doe.com",
            "reseller-admin",
            conftest.RESELLER_ID,
            status.HTTP_201_CREATED,
            "success_case",
        ),
        (
            "john@doe.com",
            "snowfall-admin",
            None,
            status.HTTP_201_CREATED,
            "success_case_no_reseller",
        ),
        (
            "bad",
            "example",
            "input",
            status.HTTP_400_BAD_REQUEST,
            "failure_case",
        ),
    ],
    ids=[
        "Create User - Success",
        "Create Snowfall User - Success",
        "Create User - Failure",
    ],
)
async def test_create_user(
    users_client: httpx.AsyncClient,
    users_repository: repository.UsersRepository,
    mock_create_user_payload: Any,
    email: str,
    role: str,
    reseller_id: str | None,
    expected_status: int,
    test_id: str,
) -> None:
    payload = mock_create_user_payload(email=email, role=role, reseller_id=reseller_id)
    response = await users_client.post(
        "/users",
        json={"data": payload},
        headers={"Content-Type": "application/vnd.api+json"},
    )
    assert response.status_code == expected_status, "Test ID: {0} failed.".format(
        test_id,
    )
    if expected_status == status.HTTP_201_CREATED:
        user = response.json()["data"]
        hub_user = await users_repository.find_by_ory_identity_id(user["id"])
        assert hub_user

        if reseller_id:
            response_reseller_id = user["relationships"]["reseller"]["data"]["id"]
            assert response_reseller_id
            assert hub_user.reseller_id == response_reseller_id


async def test_get_user(
    client: httpx.AsyncClient,
    ory_identities: Sequence[identities_pb2.Identity],
) -> None:
    ory_user = copy.copy(ory_identities[0])
    response = await client.get(
        "/users/{0}".format(ory_user.id),
        headers={"Content-Type": "application/vnd.api+json"},
    )

    response_data = response.json()["data"]
    assert response_data["id"] == ory_user.id
    assert response_data["attributes"]["email"] == ory_user.email
    assert response_data["attributes"]["role"] == ory_user.metadata_public["role"]
    assert (
        response_data["relationships"]["reseller"]["data"]["id"]
        == ory_identities[0].metadata_public["reseller_id"]
    )


async def test_delete_user(
    users_client: httpx.AsyncClient,
    ory_identities: Sequence[identities_pb2.Identity],
    users_repository: repository.UsersRepository,
) -> None:
    user = ory_identities[0]
    response = await users_client.delete(
        "/users/{0}".format(user.id),
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    hub_user = await users_repository.find_by_ory_identity_id(user.id)

    assert not hub_user


@pytest.mark.parametrize(
    ("identity_id", "reseller_id", "test_id"),
    [
        (
            conftest.IDENTITIY_IDS[0],
            "some-new-reseller-id",
            "success_case",
        ),
        (
            conftest.IDENTITIY_IDS[1],
            None,
            "success_case_no_user",
        ),
    ],
    ids=[
        "Update User - Success",
        "Update User Doesnt Exist - Success",
    ],
)
async def test_update_user(  # noqa: WPS218
    users_client: httpx.AsyncClient,
    mock_create_user_payload: Any,
    ory_identities: Sequence[identities_pb2.Identity],
    users_repository: repository.UsersRepository,
    identity_id: identities_pb2.Identity,
    reseller_id: str | None,
    test_id: str,
) -> None:
    user = next(identity for identity in ory_identities if identity.id == identity_id)
    user.email = "somenewemail@email.com"
    user_metadata = dict(user.metadata_public.items())
    user_role = user_metadata.get("role", "")

    payload = mock_create_user_payload(
        email=user.email,
        role=user_role,
        reseller_id=reseller_id,
    )
    response = await users_client.patch(
        url="/users/{0}".format(user.id),
        json={"data": payload},
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_200_OK, "Test ID: {0} failed.".format(
        test_id,
    )

    response_data = response.json()["data"]

    assert response_data["id"] == user.id
    assert response_data["attributes"]["email"] == user.email
    assert response_data["attributes"]["role"] == user_role

    hub_user = await users_repository.find_by_ory_identity_id(user.id)
    assert hub_user

    if reseller_id:
        assert response_data["relationships"]["reseller"]["data"]["id"] == reseller_id
        assert hub_user.reseller_id == reseller_id


async def test_list_users(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/users")
    users = response.json()["data"]

    assert response.status_code == status.HTTP_200_OK
    assert len(users) == 2
    for user in users:
        assert user["id"] in conftest.IDENTITIY_IDS


async def test_list_users_for_reseller_user(
    users_client: httpx.AsyncClient,
) -> None:
    response = await users_client.get("/users")
    users = response.json()["data"]

    assert response.status_code == status.HTTP_200_OK
    assert len(users) == 1
    assert users[0]["id"] == conftest.IDENTITIY_IDS[0]


class TestUserDataIncludesCompanyAndContacts(object):
    async def test_user_data_includes_company_and_contacts(
        self,
        users_client: httpx.AsyncClient,
    ) -> None:
        resp = await users_client.get("/users/me")
        assert resp.status_code == status.HTTP_200_OK

        body = resp.json()
        user_data = body["data"]

        assert user_data["id"] == conftest.RESELLER_ID
        assert user_data["attributes"]["company"]["name"] == "Company name"
        assert len(user_data["attributes"]["contacts"]) == 1
