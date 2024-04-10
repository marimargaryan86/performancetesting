import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestGetPlace:
    async def test_get_place_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/places/{placeId}".format(
                placeId=fixtures.PLACES[0],
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_place_should_fail_when_not_existing_place_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places/{placeId}".format(
                placeId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_place_is_successful(  # noqa: WPS218
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places/{placeId}".format(
                placeId=fixtures.PLACES[0],
            ),
        )

        response_data = response.json()["data"]
        search_capabilities = response_data["attributes"]["searchCapabilities"]

        assert response.status_code == status.HTTP_200_OK
        assert response_data["id"] == fixtures.PLACES[0]
        assert search_capabilities["air"] is True
        assert search_capabilities["ferry"] is False
        assert search_capabilities["rail"] is True
        assert "city" in response_data["relationships"]
        assert "contains" in response_data["relationships"]
