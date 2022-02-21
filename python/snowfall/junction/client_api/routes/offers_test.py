import pytest
from starlette import status, testclient

from snowfall import fixtures


@pytest.mark.asyncio
class TestOfferSearches(object):
    async def test_offer_search_unknown_trip_returns_error(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "age": 42,
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.NOT_FOUND,
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_offer_search_can_be_created(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "age": 42,
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.TRIP,
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED
