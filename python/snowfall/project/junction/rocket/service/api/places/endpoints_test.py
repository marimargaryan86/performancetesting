from collections.abc import Mapping
from typing import Any

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
        assert search_capabilities["flight"] is True
        assert search_capabilities["ferry"] is False
        assert search_capabilities["train"] is True
        assert "city" in response_data["relationships"]
        assert "contains" in response_data["relationships"]


class TestGetPlaces:
    async def test_get_place_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/places",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_place_should_fail_when_not_existing_place_iata_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places",
            params={"filter[iata][eq]": fixtures.NOT_FOUND_PLACE_IATA},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_place_by_iata_is_successful(  # noqa: WPS218
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places",
            params={"filter[iata][eq]": fixtures.PLACE_IATAS[0]},
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["data"]
        for place in response_data:
            self._validate_place(place)

    async def test_get_place_should_fail_when_not_existing_place_filter_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places",
            params={"filter[name][like]": fixtures.NOT_FOUND_PLACE_NAME},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_place_filter_is_successful(  # noqa: WPS218
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/places",
            params={
                "filter[name][like]": fixtures.PLACE_NAMES[0],
                "query[coordinates]": "1,1,1",
                "filter[type][eq]": "city",
                "query[placeToSearchWithin]": "799d5f9f-ab7d-4c97-a866-da6e57875854",
                "page[limit]": 5,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["data"]
        for place in response_data:
            self._validate_place(place)

    def _validate_place(self, place: Mapping[str, Any]) -> None:
        search_capabilities = place["attributes"]["searchCapabilities"]
        assert place["id"] == fixtures.PLACES[0]
        assert search_capabilities == {"flight": True, "ferry": False, "train": True}
        assert "city" in place["relationships"]
        assert "contains" in place["relationships"]
