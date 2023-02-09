from typing import Type

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import status
from fastapi.testclient import TestClient


async def test_can_get_accounts(
    client: TestClient,
    account_factory: Type[AsyncSQLAlchemyFactory],
) -> None:
    account = await account_factory.create()
    response = client.get("/accounts")

    assert response.status_code == status.HTTP_200_OK
    assert account.email == response.json()[0]["email"]
