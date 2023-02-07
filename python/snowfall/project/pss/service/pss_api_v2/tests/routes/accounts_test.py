from fastapi import status
from fastapi.testclient import TestClient


def test_can_get_accounts(client: TestClient) -> None:
    response = client.get("/accounts")

    assert response.status_code == status.HTTP_200_OK
