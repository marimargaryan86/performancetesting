from typing import Type, cast
from unittest.mock import create_autospec

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.schemas.errors import FAIL
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


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


async def test_can_initiate_forgot_password_if_account_exists(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
    account_forgotten_password_factory: Type[AsyncSQLAlchemyFactory],
    db_session: AsyncSession,
) -> None:
    mock_smtp_email_service = create_autospec(SMTPEmailService, spec_set=True)
    cast(FastAPI, client.app).dependency_overrides[
        SMTPEmailService
    ] = mock_smtp_email_service

    account = await account_factory.create()
    await account_forgotten_password_factory.create_batch(
        size=2,
        account_id=account.id,
    )

    payload = {"email": account.email}
    response = client.post("/accounts/forgotpassword", json=payload)

    assert response.status_code == status.HTTP_200_OK

    async with db_session as session:
        async with session.begin():
            statement = select(AccountForgottenPassword).filter(
                AccountForgottenPassword.used == False,  # noqa:E712
            )
            res = await session.execute(statement)
            latest_account_forgotten_password = res.scalars().first()
            statement = select(AccountForgottenPassword).filter(
                AccountForgottenPassword.used == True,  # noqa:E712
            )
            res = await session.execute(statement)
            used_account_forgotten_password_count = len(res.scalars().all())

    assert latest_account_forgotten_password

    mock_smtp_email_service().send_forgotten_password_email.assert_called_once_with(
        token=latest_account_forgotten_password.token,
        recipient=account.email,
    )

    assert used_account_forgotten_password_count == 2


async def test_cant_initiate_forgot_password_if_account_doesnt_exist(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
    account_forgotten_password_factory: Type[AsyncSQLAlchemyFactory],
    db_session: AsyncSession,
) -> None:
    mock_smtp_email_service = create_autospec(SMTPEmailService, spec_set=True)
    cast(FastAPI, client.app).dependency_overrides[
        SMTPEmailService
    ] = mock_smtp_email_service

    await account_forgotten_password_factory.create_batch(
        size=2,
        account_id=1,
    )

    payload = {"email": "nonexistent@email.com"}
    response = client.post("/accounts/forgotpassword", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    async with db_session as session:
        async with session.begin():
            statement = select(AccountForgottenPassword)
            res = await session.execute(statement)
            forgotten_passwords_count = len(res.scalars().all())

    mock_smtp_email_service().send_forgotten_password_email.assert_not_called()

    assert forgotten_passwords_count == 2
