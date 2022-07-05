from starlette import status, testclient

from snowfall import fixtures


class TestPlaces(object):
    def test_unknown_place_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/places/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_place_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/places/{id}".format(id=fixtures.PLACES[0]))
        assert response.status_code == status.HTTP_200_OK

    def test_multiple_places_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/places")
        assert response.status_code == status.HTTP_200_OK
