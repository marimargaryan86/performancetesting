from starlette import status, testclient

from snowfall import fixtures
from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.format.protobuf import enum_value_to_slug


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

    def test_leg_type_is_found(self, client: testclient.TestClient) -> None:
        schedule_type_id = enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        response = client.get("/legs/types/{id}".format(id=schedule_type_id))
        assert response.status_code == status.HTTP_200_OK

    def test_leg_type_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "{0}f".format(client.headers["Authorization"])
        schedule_type_id = enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        response = client.get("/legs/types/{id}".format(id=schedule_type_id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unknown_leg_type_is_not_found(self, client: testclient.TestClient) -> None:
        response = client.get("/legs/types/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

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
