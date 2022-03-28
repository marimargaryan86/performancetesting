from starlette import status, testclient

from snowfall import fixtures


class TestLegs(object):
    def test_unknown_leg_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/legs/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_leg_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/legs/{id}".format(id=fixtures.LEGS[0]))
        assert response.status_code == status.HTTP_200_OK
