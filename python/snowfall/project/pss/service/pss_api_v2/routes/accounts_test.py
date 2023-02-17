from typing import Type

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import status
from fastapi.testclient import TestClient

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.schemas.errors import FAIL


async def test_can_get_accounts(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.get("/accounts")

    assert response.status_code == status.HTTP_200_OK
    assert account.email == response.json()[0]["email"]


async def test_can_not_login_if_not_existed_account_provided(
    client: TestClient,
) -> None:
    payload = {"email": "test@account.com", "password": "test"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_FOUND


async def test_can_not_login_if_account_is_not_active(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create(active=False)
    payload = {"email": account.email, "password": "test_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_ACTIVE


async def test_can_not_login_if_wrong_password_provided(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    payload = {"email": account.email, "password": "wrong_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_PASSWORD_DONT_MATCH


async def test_can_login_account(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    payload = {"email": account.email, "password": "test_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == account.email
    assert response.json()["active"] is True
