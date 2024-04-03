from typing import Any

import httpx
from starlette import status

_PLACES_URL = "/places"


class TestPlaces:
    async def test_get_places(
        self,
        authenticated_http_client: httpx.AsyncClient,
        places_fixture: Any,
    ) -> None:
        response = await authenticated_http_client.get(
            "{base}".format(base=_PLACES_URL),
        )

        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert len(response_json["data"]) == len(places_fixture)

    async def test_places_exact_match(
        self,
        authenticated_http_client: httpx.AsyncClient,
        places_fixture: Any,
    ) -> None:
        place_to_find = places_fixture[len(places_fixture) // 2]["name"]
        response = await authenticated_http_client.get(
            "{base}?query[name]={query}".format(
                base=_PLACES_URL,
                query=place_to_find,
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["data"]
        assert response_data
        assert response_data[0]["attributes"]["name"] == place_to_find
