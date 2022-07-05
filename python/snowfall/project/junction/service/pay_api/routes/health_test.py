from starlette import status, testclient


class TestHealth(object):
    def test_health_status_code(self, http_client: testclient.TestClient) -> None:
        response = http_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
