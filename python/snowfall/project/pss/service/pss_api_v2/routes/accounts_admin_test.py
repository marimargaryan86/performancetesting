from typing import Type

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import status
from fastapi.testclient import TestClient

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.schemas.errors import FAIL


async def test_admin_can_not_login_if_not_existed_account_provided(
    client: TestClient,
) -> None:
    payload = {"email": "test@account.com", "password": "test"}
    response = client.post("/admin/login", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_FOUND


async def test_admin_can_not_login_if_account_is_not_active(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    admin_account = await account_factory.create(active=False)
    payload = {"email": admin_account.email, "password": "test_password"}
    response = client.post("/admin/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_ACTIVE


async def test_admin_can_not_login_if_wrong_password_provided(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    admin_account = await account_factory.create()
    payload = {"email": admin_account.email, "password": "wrong_password"}
    response = client.post("/admin/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_PASSWORD_DONT_MATCH


async def test_admin_can_not_login_if_has_no_permissions(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    admin_account = await account_factory.create()
    payload = {"email": admin_account.email, "password": "test_password"}
    response = client.post("/admin/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_ALLOWED


async def test_admin_can_login(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    admin_account = await account_factory.create(
        admin=True,
        staff=True,
        support=True,
        flirtboard=True,
        stadler=True,
        operator=True,
    )
    payload = {"email": admin_account.email, "password": "test_password"}
    response = client.post("/admin/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == admin_account.email
    assert response.json()["active"] is True
