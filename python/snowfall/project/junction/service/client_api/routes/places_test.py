from starlette import status, testclient

from snowfall import fixtures
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette.routes import testing
from snowfall.stdlib.v1alpha import models_pb2


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
        client.headers["Authorization"] = "invalid"
        response = client.get("/places")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_place_types(self, client: testclient.TestClient) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/places/types",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    descriptor=models_pb2.Place.Type.DESCRIPTOR,
                    enum_value=place_type,
                )
                for place_type in models_pb2.Place.Type.values()
            ],
        )
