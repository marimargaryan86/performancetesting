from typing import Any

from starlette import status, testclient

_PLACES_URL = "/places"


class TestPlaces(object):
    def test_get_places(
        self,
        authenticated_http_client: testclient.TestClient,
        places_fixture: Any,
    ) -> None:
        response = authenticated_http_client.get("{base}".format(base=_PLACES_URL))

        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert len(response_json["data"]) == len(places_fixture)

    def test_places_exact_match(
        self,
        authenticated_http_client: testclient.TestClient,
        places_fixture: Any,
    ) -> None:
        place_to_find = places_fixture[len(places_fixture) // 2]["name"]
        response = authenticated_http_client.get(
            "{base}?query[name]={query}".format(
                base=_PLACES_URL,
                query=place_to_find,
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["data"]
        assert response_data
        assert response_data[0]["attributes"]["name"] == place_to_find
