from collections.abc import Sequence
from typing import Any

import httpx
import pytest
from starlette import status

from snowfall.project.junction.hub.service.hub_api.conftest import RESELLER_ID
from snowfall.service.authentication.v1 import identities_pb2


@pytest.mark.parametrize(
    ("email", "role", "reseller_id", "expected_status", "test_id"),
    [
        (
            "john@doe.com",
            "reseller-admin",
            RESELLER_ID,
            status.HTTP_201_CREATED,
            "success_case",
        ),
        (
            "bad",
            "example",
            "input",
            status.HTTP_400_BAD_REQUEST,
            "failure_case",
        ),
    ],
    ids=["Create User - Success", "Create User - Failure"],
)
async def test_create_user(
    client: httpx.AsyncClient,
    mock_create_user_payload: Any,
    email: str,
    role: str,
    reseller_id: str,
    expected_status: int,
    test_id: str,
) -> None:
    payload = mock_create_user_payload(email=email, role=role, reseller_id=reseller_id)
    response = await client.post(
        "/users",
        json={"data": payload},
        headers={"Content-Type": "application/vnd.api+json"},
    )
    assert response.status_code == expected_status, "Test ID: {0} failed.".format(
        test_id,
    )


async def test_delete_user(
    client: httpx.AsyncClient,
    ory_users: Sequence[identities_pb2.Identity],
) -> None:
    response = await client.delete(
        "/users/{0}".format(ory_users[0].id),
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUserDataIncludesCompanyAndContacts(object):
    async def test_user_data_includes_company_and_contacts(
        self,
        users_client: httpx.AsyncClient,
    ) -> None:
        resp = await users_client.get("/users/me")
        assert resp.status_code == status.HTTP_200_OK

        body = resp.json()
        user_data = body["data"]

        assert user_data["id"] == RESELLER_ID
        assert user_data["attributes"]["company"]["name"] == "Company name"
        assert len(user_data["attributes"]["contacts"]) == 1
