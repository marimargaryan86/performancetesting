from starlette import status, testclient


class TestHealth(object):
    def test_health_status_code(self, client: testclient.TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
