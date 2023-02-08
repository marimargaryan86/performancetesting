from typing import Type

from factory.alchemy import SQLAlchemyModelFactory
from fastapi import status
from fastapi.testclient import TestClient


def test_can_get_accounts(
    client: TestClient,
    account_factory: Type[SQLAlchemyModelFactory],
) -> None:
    account = account_factory.create()
    response = client.get("/accounts")

    assert response.status_code == status.HTTP_200_OK
    assert account.email == response.json()[0]["email"]
