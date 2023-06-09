import datetime
from typing import cast
from unittest.mock import create_autospec

import bcrypt
import freezegun
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.schemas.responses import FAIL
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


async def test_can_get_accounts(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.get("/accounts")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert account.email == response.json()["data"][0]["email"]


async def test_can_not_get_current_account_if_not_authenticated(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    await account_factory.create()
    response = client.get("/accounts/me", headers={"x-auth-token": "non_existed_token"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_can_get_current_account(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.get("/accounts/me", headers={"x-auth-token": account.token})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == account.email


async def test_should_fail_on_email_update_if_email_is_already_taken(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    existing_account = await account_factory.create()
    new_account = await account_factory.create()
    response = client.post(
        "/accounts/update",
        headers={"x-auth-token": new_account.token},
        json={"email": existing_account.email},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["message"] == messages.ACCOUNT_EMAIL_ALREADY_EXISTS


async def test_can_update_email(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.post(
        "/accounts/update",
        headers={"x-auth-token": account.token},
        json={"email": "updated_test@email.com"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == "updated_test@email.com"


async def test_can_update_password(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.post(
        "/accounts/update",
        headers={"x-auth-token": account.token},
        json={"password": "updated_password"},
    )

    assert response.status_code == status.HTTP_200_OK


async def test_can_update_account(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    payload = {
        "firstname": "test_firstname",
        "lastname": "test_surname",
        "mobile": "+44019020030",
    }

    response = client.post(
        "/accounts/update",
        headers={"x-auth-token": account.token},
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["firstname"] == payload["firstname"]
    assert response.json()["data"]["lastname"] == payload["lastname"]
    assert response.json()["data"]["mobile"] == payload["mobile"]


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
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create(active=False)
    payload = {"email": account.email, "password": "test_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_NOT_ACTIVE


async def test_can_not_login_if_wrong_password_provided(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    payload = {"email": account.email, "password": "wrong_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["status"] == FAIL
    assert response.json()["message"] == messages.ACCOUNT_PASSWORD_DONT_MATCH


async def test_can_login_account(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    payload = {"email": account.email, "password": "test_password"}
    response = client.post("/accounts/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == account.email
    assert response.json()["data"]["active"] is True


async def test_can_initiate_forgot_password_if_account_exists(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
    account_forgotten_password_factory: type[AsyncSQLAlchemyFactory],
    db_session: async_sessionmaker[AsyncSession],
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

    async with db_session() as session:
        statement = select(AccountForgottenPassword).filter(
            AccountForgottenPassword.used == False,  # noqa: E712
        )
        res = await session.execute(statement)
        latest_account_forgotten_password = res.scalars().first()
        statement = select(AccountForgottenPassword).filter(
            AccountForgottenPassword.used == True,  # noqa: E712
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
    account_factory: type[AsyncSQLAlchemyFactory],
    account_forgotten_password_factory: type[AsyncSQLAlchemyFactory],
    db_session: async_sessionmaker[AsyncSession],
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

    async with db_session() as session:
        statement = select(AccountForgottenPassword)
        res = await session.execute(statement)
        forgotten_passwords_count = len(res.scalars().all())

    mock_smtp_email_service().send_forgotten_password_email.assert_not_called()

    assert forgotten_passwords_count == 2


async def test_can_reset_password_if_token_unused_and_not_expired(
    client: TestClient,
    account_factory: type[AsyncSQLAlchemyFactory],
    account_forgotten_password_factory: type[AsyncSQLAlchemyFactory],
    db_session: async_sessionmaker[AsyncSession],
) -> None:
    account = await account_factory.create()
    account_forgotten_password = await account_forgotten_password_factory.create(
        account_id=account.id,
    )

    raw_password = "test-password"  # nosec
    payload = {
        "token": account_forgotten_password.token,
        "password": raw_password,
    }  # nosec
    response = client.post("/accounts/resetpassword", json=payload)

    assert response.status_code == status.HTTP_200_OK

    async with db_session() as session:
        statement = select(Account).filter(Account.id == account.id)
        res = await session.execute(statement)
        updated_account = res.scalars().first()
        assert updated_account
        statement = select(AccountForgottenPassword).filter(
            AccountForgottenPassword.token == account_forgotten_password.token,
        )
        res = await session.execute(statement)
        updated_account_forgotten_password = res.scalars().first()
        assert updated_account_forgotten_password

    assert bcrypt.checkpw(raw_password.encode(), updated_account.password.encode())
    assert updated_account_forgotten_password.used


async def test_cant_reset_password_if_token_doesnt_exist(
    client: TestClient,
) -> None:
    payload = {
        "token": "fake-token",
        "password": "not-used",
    }  # nosec

    response = client.post("/accounts/resetpassword", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == (
        messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_NOT_FOUND
    )


async def test_cant_reset_password_if_token_already_used(
    client: TestClient,
    account_forgotten_password_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    token = "test-token"  # nosec
    await account_forgotten_password_factory.create(token=token, used=True)  # nosec
    payload = {
        "token": token,
        "password": "not-used",
    }  # nosec

    response = client.post("/accounts/resetpassword", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["message"] == (
        messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_ALREADY_USED
    )


@freezegun.freeze_time("2023-01-01 01:01:00")
async def test_cant_reset_password_if_token_expired(
    client: TestClient,
    account_forgotten_password_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    token = "test-token"  # nosec
    await account_forgotten_password_factory.create(
        token=token,
        used=False,
        created=datetime.datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
    )
    payload = {
        "token": token,
        "password": "not-used",
    }  # nosec

    response = client.post("/accounts/resetpassword", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["message"] == (
        messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_EXPIRED
    )
