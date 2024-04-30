import datetime
from collections.abc import Mapping
from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestTrainCreateSearch:
    @property
    def search_payload(self) -> Mapping[str, Any]:
        tomorrow = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        return {
            "data": {
                "type": "train-searches",
                "attributes": {
                    "departureAfter": tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "returnAt": after_tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "passengers": [{"dateOfBirth": "2000-01-01"}],
                },
                "relationships": {
                    "origin": {
                        "data": {
                            "id": fixtures.PLACES[0],
                            "type": "places",
                        },
                    },
                    "destination": {
                        "data": {
                            "id": fixtures.PLACES[0],
                            "type": "places",
                        },
                    },
                },
            },
        }

    async def test_create_trains_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/trains/searches",
            json=self.search_payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["id"]

    async def test_create_trains_search_fails_when_origin_does_not_exist(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        origin = payload["data"]["relationships"]["origin"]
        origin["data"]["id"] = fixtures.NOT_FOUND

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_fails_when_destination_does_not_exist(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        destination = payload["data"]["relationships"]["destination"]
        destination["data"]["id"] = fixtures.NOT_FOUND

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_departure_after_in_past_throws_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["departureAfter"] = "1998-04-05T08:00:00Z"

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_return_at_in_past_throws_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["returnAt"] = "1998-04-05T08:00:00Z"

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_return_at_before_departure_at_throws_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        return_at = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=1)
        payload["data"]["attributes"]["returnAt"] = return_at.strftime(
            "%Y-%m-%dT08:00:00.000Z",
        )

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_departure_before_in_past_throws_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["departureBefore"] = "1998-04-05T08:00:00Z"

        await self._assert_unprocessable_entity(client, payload)

    async def test_create_trains_search_return_at_before_departure_before_throws_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        departure_before = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
            days=2,
        )
        payload["data"]["attributes"]["departureBefore"] = departure_before.strftime(
            "%Y-%m-%dT08:00:00.000Z",
        )

        await self._assert_unprocessable_entity(client, payload)

    async def _assert_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
        payload: Mapping[str, Any],
    ) -> None:
        response = await client.post(
            "/trains/searches",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTrainGetSearch:
    async def test_get_trains_search_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/trains/searches/{searchId}".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_trains_search_should_fail_when_not_existing_search_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/searches/{searchId}".format(
                searchId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_trains_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/searches/{searchId}".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK


class TestTrainListSearchResults:
    async def test_list_trains_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/searches/{searchId}/results".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

    async def test_list_trains_search_results_with_includes_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/searches/{searchId}/results".format(
                searchId=fixtures.RAIL_SEARCH_ID,
            ),
            params={"include": "offers,resultDetails"},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

        included_types = [resource["type"] for resource in results["included"]]
        assert "train-offers" in included_types
        assert "train-result-details" in included_types


class TestTrainGetOffer:
    async def test_get_trains_offer_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/trains/offers/{offerId}".format(
                offerId=fixtures.RAIL_OFFERS[0],
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_trains_offer_should_fail_when_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/offers/{offerId}".format(
                offerId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_trains_offer_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trains/offers/{offerId}".format(
                offerId=fixtures.RAIL_OFFERS[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_rail_offer_should_fail_when_wrong_offer_type(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/rail/offers/{offerId}".format(
                offerId=fixtures.CAR_RENTAL_OFFERS[0],
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
