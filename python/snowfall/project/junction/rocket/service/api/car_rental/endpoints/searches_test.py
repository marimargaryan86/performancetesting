import datetime
from collections.abc import Mapping
from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestCarRentalCreateSearch:
    @property
    def search_payload(self) -> Mapping[str, Any]:
        tomorrow = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        return {
            "data": {
                "type": "car-searches",
                "attributes": {
                    "driverAge": 28,
                    "pickupAt": tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "returnAt": after_tomorrow.strftime("%Y-%m-%dT08:00:00.000Z"),
                    "pickupLocation": {
                        "latitude": 50.89369066956447,
                        "longitude": 4.47136870945399,
                    },
                    "returnLocation": {
                        "latitude": 48.96691462802318,
                        "longitude": 2.52817297961273,
                    },
                },
            },
        }

    async def test_create_car_rental_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/car-rental/searches",
            json=self.search_payload,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["id"]

    async def test_create_car_rental_invalid_pickup_latitude(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["pickupLocation"]["latitude"] = -91
        await self._assert_bad_request(client, payload)

    async def test_create_car_rental_invalid_pickup_longitude(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["pickupLocation"]["longitude"] = -200
        await self._assert_bad_request(client, payload)

    async def test_create_car_rental_invalid_return_latitude(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["returnLocation"]["latitude"] = 91
        await self._assert_bad_request(client, payload)

    async def test_create_car_rental_invalid_return_longitude(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["returnLocation"]["longitude"] = 200
        await self._assert_bad_request(client, payload)

    async def test_create_car_rental_invalid_driver_age(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["driverAge"] = 14
        await self._assert_bad_request(client, payload)

    async def test_create_car_rental_invalid_pickup_date(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["pickupAt"] = "1998-04-05T08:00:00Z"
        await self._assert_unprocessable_entity(client, payload)

    async def test_create_car_rental_invalid_return_date(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        payload["data"]["attributes"]["returnAt"] = "1998-04-05T08:00:00Z"
        await self._assert_unprocessable_entity(client, payload)

    async def test_create_car_rental_invalid_pickup_and_return_sequence(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = self.search_payload
        tomorrow = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        payload["data"]["attributes"]["pickupAt"] = after_tomorrow.strftime(
            "%Y-%m-%dT08:00:00.000Z",
        )
        payload["data"]["attributes"]["returnAt"] = tomorrow.strftime(
            "%Y-%m-%dT08:00:00.000Z",
        )
        await self._assert_unprocessable_entity(client, payload)

    async def _assert_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
        payload: Mapping[str, Any],
    ) -> None:
        response = await client.post(
            "/car-rental/searches",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def _assert_bad_request(
        self,
        client: httpx.AsyncClient,
        payload: Mapping[str, Any],
    ) -> None:
        response = await client.post(
            "/car-rental/searches",
            json=payload,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCarRentalGetSearch:
    async def test_get_car_rental_search_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.CAR_RENTAL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_car_rental_search_should_fail_when_not_existing_search_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_car_rental_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.CAR_RENTAL_SEARCH_ID,
            ),
        )

        assert response.status_code == status.HTTP_200_OK


class TestCarRentalListSearchResults:
    async def test_list_car_rental_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}/results".format(
                searchId=fixtures.CAR_RENTAL_SEARCH_ID,
            ),
            params={"include": "offers,resultDetails"},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2

        included_types = [resource["type"] for resource in results["included"]]
        assert "offers" in included_types
        assert "result-details" in included_types
