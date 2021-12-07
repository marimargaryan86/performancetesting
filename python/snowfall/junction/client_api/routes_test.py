from starlette import status, testclient


def test_health_status_code(client: testclient.TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
