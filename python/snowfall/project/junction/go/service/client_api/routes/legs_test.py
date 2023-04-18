import httpx
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import testing
from snowfall.stdlib.v1alpha import models_pb2


class TestLegs(object):
    async def test_unknown_leg_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/legs/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_leg_is_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/legs/{id}".format(id=fixtures.LEGS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_leg_unauthorized(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.get("/legs/{id}".format(id=fixtures.LEGS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_leg_types(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/legs/types",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                    enum_value=leg_type,
                )
                for leg_type in models_pb2.Schedule.Type.values()
            ],
        )

    async def test_segment_legs_are_not_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/segments/{id}/legs".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_segment_legs_are_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get(
            "/segments/{id}/legs".format(id=fixtures.SEGMENTS[0]),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_segment_legs_unauthorized(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.get(
            "/segments/{id}/legs".format(id=fixtures.SEGMENTS[0]),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_trip_legs_are_not_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/trips/{id}/legs".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_trip_legs_are_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/trips/{id}/legs".format(id=fixtures.TRIPS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_trip_legs_unauthorized(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.get("/trips/{id}/legs".format(id=fixtures.TRIPS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_legs_by_trip_search_ids_are_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/searches/{id}/legs".format(id=fixtures.TRIPS[0]),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_legs_by_trip_search_with_no_trips(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/searches/{id}/legs".format(id=fixtures.TRIP_SEARCHES[0]),
        )
        assert response.status_code == status.HTTP_200_OK
        assert not response.json()["data"]
