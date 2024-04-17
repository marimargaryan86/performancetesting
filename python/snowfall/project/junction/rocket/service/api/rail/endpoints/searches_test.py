import typing
import uuid

import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestRailCreateSearch:
    @property
    def payload(self) -> typing.Mapping[str, typing.Any]:
        return {
            "data": {
                "type": "rail-searches",
                "attributes": {
                    "departureAfter": "2024-04-05T08:00:00Z",
                    "departureBefore": "2024-04-05T08:00:00Z",
                    "returnAt": "2024-04-07T08:00:00Z",
                    "passengers": [{"dateOfBirth": "2000-01-01"}],
                },
                "relationships": {
                    "origin": {
                        "data": {
                            "id": "3debfa7c-9884-5409-86c8-33f3e491382e",
                            "type": "places",
                        },
                    },
                    "destination": {
                        "data": {
                            "id": "3debfa7c-9884-5409-86c8-33f3e491382e",
                            "type": "places",
                        },
                    },
                },
            },
        }

    async def test_create_rail_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.payload

        response = await client.post(
            "/rail/searches",
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["id"]

    async def test_create_rail_search_fails_when_origin_does_not_exist(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.payload
        origin = payload["data"]["relationships"]["origin"]
        origin["data"]["id"] = str(
            uuid.uuid4(),
        )

        response = await client.post(
            "/rail/searches",
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.json()["errors"][0]["source"]["pointer"]
            == "/data/relationships/origin"
        )

    async def test_create_rail_search_fails_when_destination_does_not_exist(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.payload
        destination = payload["data"]["relationships"]["destination"]
        destination["data"]["id"] = str(
            uuid.uuid4(),
        )

        response = await client.post(
            "/rail/searches",
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.json()["errors"][0]["source"]["pointer"]
            == "/data/relationships/destination"
        )


class TestRailGetSearch:
    async def test_get_rail_search_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/rail/searches/{searchId}".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_rail_search_should_fail_when_not_existing_search_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/rail/searches/{searchId}".format(
                searchId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_rail_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/rail/searches/{searchId}".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK


class TestRailListSearchResults:
    async def test_list_rail_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/rail/searches/{searchId}/results".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

    async def test_list_rail_search_results_with_includes_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/rail/searches/{searchId}/results".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
            params={"include": "offers,resultDetails"},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

        included_types = [resource["type"] for resource in results["included"]]
        assert "rail-offers" in included_types
        assert "rail-result-details" in included_types
