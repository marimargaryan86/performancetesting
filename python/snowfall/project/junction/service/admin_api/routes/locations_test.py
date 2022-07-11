from starlette import status, testclient

from snowfall import fixtures


class TestLocations(object):
    def test_unknown_location_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/locations/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_location_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/locations/{id}".format(id=fixtures.LOCATIONS[0]))
        assert response.status_code == status.HTTP_200_OK

    def test_multiple_locations_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/locations")
        assert response.status_code == status.HTTP_200_OK
