from starlette import status, testclient

from snowfall import fixtures
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette.routes import testing
from snowfall.stdlib.v1alpha import models_pb2


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

    def test_leg_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        response = client.get("/legs/{id}".format(id=fixtures.LEGS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_leg_types(self, client: testclient.TestClient) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/legs/types",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                    enum_value=leg_type,
                )
                for leg_type in models_pb2.Schedule.Type.values()
            ],
        )

    def test_segment_legs_are_not_found(self, client: testclient.TestClient) -> None:
        response = client.get("/segments/{id}/legs".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_segment_legs_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/segments/{id}/legs".format(id=fixtures.SEGMENTS[0]))
        assert response.status_code == status.HTTP_200_OK

    def test_segment_legs_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        response = client.get("/segments/{id}/legs".format(id=fixtures.SEGMENTS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_trip_legs_are_not_found(self, client: testclient.TestClient) -> None:
        response = client.get("/trips/{id}/legs".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_trip_legs_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/trips/{id}/legs".format(id=fixtures.TRIPS[0]))
        assert response.status_code == status.HTTP_200_OK

    def test_trip_legs_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        response = client.get("/trips/{id}/legs".format(id=fixtures.TRIPS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_legs_by_trip_search_ids_are_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/trips/searches/{id}/legs".format(id=fixtures.TRIPS[0]))
        assert response.status_code == status.HTTP_404_NOT_FOUND
