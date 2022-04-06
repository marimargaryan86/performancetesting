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

    def test_leg_type_is_found(self, client: testclient.TestClient) -> None:
        schedule_type_id = enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        response = client.get("/legs/types/{id}".format(id=schedule_type_id))
        assert response.status_code == status.HTTP_200_OK

    def test_unknown_leg_type_is_not_found(self, client: testclient.TestClient) -> None:
        response = client.get("/legs/types/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND
