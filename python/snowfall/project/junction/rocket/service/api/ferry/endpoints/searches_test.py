import datetime
from collections.abc import Mapping
from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestFerryCreateSearch:
    @property
    def search_payload(self) -> Mapping[str, Any]:
        tomorrow = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        return {
            "data": {
                "type": "ferry-searches",
                "attributes": {
                    "departureAfter": tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "returnAt": after_tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "origin": {
                        "latitude": 50.89369066956447,
                        "longitude": 4.47136870945399,
                    },
                    "destination": {
                        "latitude": 48.96691462802318,
                        "longitude": 2.52817297961273,
                    },
                    "passengers": [{"dateOfBirth": "2000-01-01"}],
                },
            },
        }

    async def test_create_ferry_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/ferry/searches",
            json=self.search_payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["id"]

    async def test_create_ferry_search_departure_after_in_past_throws_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["departureAfter"] = "1998-04-05T08:00:00Z"

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_ferry_search_return_at_in_past_throws_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["returnAt"] = "1998-04-05T08:00:00Z"

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_ferry_search_return_at_before_departure_at_throws_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        return_at = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=1)
        payload["data"]["attributes"]["returnAt"] = return_at.strftime(
            "%Y-%m-%dT08:00:00.000Z",
        )

        await self._assert_unprocessable_entity(client, payload)

    async def _assert_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
        payload: Mapping[str, Any],
    ) -> None:
        response = await client.post(
            "/ferry/searches",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestFerryGetSearch:
    async def test_get_ferry_search_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/ferry/searches/{searchId}".format(
                searchId=fixtures.FERRY_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_ferry_search_should_fail_when_not_existing_search_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/ferry/searches/{searchId}".format(
                searchId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_ferry_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/ferry/searches/{searchId}".format(
                searchId=fixtures.FERRY_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK


class TestListSearchResults:
    async def test_list_ferry_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/ferry/searches/{searchId}/results".format(
                searchId=fixtures.FERRY_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

    async def test_list_ferry_search_results_with_includes_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/ferry/searches/{searchId}/results".format(
                searchId=fixtures.FERRY_SEARCH_ID,
            ),
            params={"include": "offers,resultDetails"},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

        included_types = [resource["type"] for resource in results["included"]]
        assert "ferry-offers" in included_types
        assert "ferry-result-details" in included_types
