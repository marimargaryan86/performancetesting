from starlette import status, testclient

from snowfall.junction.client_api import conftest


def test_health_status_code(client: testclient.TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_unknown_place_returns_not_found(client: testclient.TestClient) -> None:
    response = client.get("/places/{id}".format(id=conftest.PLACE_NOT_FOUND))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_place_is_found(client: testclient.TestClient) -> None:
    identifier = conftest.PLACES[0]["id"]
    response = client.get("/places/{id}".format(id=identifier))
    assert response.status_code == status.HTTP_200_OK


def test_multiple_places_are_found(client: testclient.TestClient) -> None:
    response = client.get("/places")
    assert response.status_code == status.HTTP_200_OK
