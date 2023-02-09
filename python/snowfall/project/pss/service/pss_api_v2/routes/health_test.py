from fastapi import status
from fastapi.testclient import TestClient


def test_get_health_returns_correct_json_response(client: TestClient) -> None:
    resp = client.get("/health")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json == {"message": "pass"}
