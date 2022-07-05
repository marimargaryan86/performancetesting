from starlette import status, testclient


class TestUser(object):
    def test_otp_generate_no_email(self, http_client: testclient.TestClient) -> None:
        response = http_client.post(
            "/verification-code",
            json={
                "data": {
                    "attributes": {"not-email": "random"},
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
