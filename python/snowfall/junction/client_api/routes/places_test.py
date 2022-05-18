from starlette import status, testclient

from snowfall import fixtures
from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.format.protobuf import enum_value_to_slug


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

    def test_multiple_places_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        response = client.get("/places")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_place_types_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/places/types")
        assert response.status_code == status.HTTP_200_OK

    def test_place_type_is_found(self, client: testclient.TestClient) -> None:
        place_type_id = enum_value_to_slug(
            models_pb2.Place.Type.DESCRIPTOR,
            models_pb2.Place.TYPE_UNSPECIFIED,
        )
        response = client.get("/places/types/{id}".format(id=place_type_id))
        assert response.status_code == status.HTTP_200_OK

    def test_place_type_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        place_type_id = enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_UNSPECIFIED,
        )
        response = client.get("/places/types/{id}".format(id=place_type_id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unknown_place_type_is_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/places/types/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND
