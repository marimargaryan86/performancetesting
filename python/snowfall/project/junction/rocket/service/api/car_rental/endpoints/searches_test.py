import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestCreateSearch(object):
    async def test_create_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = {
            "data": {
                "type": "car-searches",
                "attributes": {
                    "driverAge": 28,
                    "pickupAt": "2024-04-05T08:00:00Z",
                    "returnAt": "2024-04-07T08:00:00Z",
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

        response = await client.post(
            "/car-rental/searches",
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["id"]


class TestGetSearch(object):
    async def test_get_search_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.SEARCHES[0],
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_search_should_fail_when_not_existing_search_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_search_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}".format(
                searchId=fixtures.SEARCHES[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK


class TestListSearchResults(object):
    async def test_list_search_results_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/searches/{searchId}/results".format(
                searchId=fixtures.SEARCHES[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results["data"]) == 2
