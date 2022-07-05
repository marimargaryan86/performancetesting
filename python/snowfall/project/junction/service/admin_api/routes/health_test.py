from starlette import status, testclient


class TestHealth(object):
    def test_health_status_code(self, client: testclient.TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_status_code_unauthorized(
        self,
        unauthorized_client: testclient.TestClient,
    ) -> None:
        response = unauthorized_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
