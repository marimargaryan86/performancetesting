import json

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
                                "dateOfBirth": "1979-09-17",
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
                                "dateOfBirth": "1979-09-17",
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

    async def test_created_trip_offer_search_can_be_retrieved(
        self,
        client: testclient.TestClient,
    ) -> None:
        offer_search = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
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
        offer_search_id = json.loads(offer_search.content.decode())["data"]["id"]
        response = client.get(
            "/offers/searches/{id}".format(id=offer_search_id),
        )
        assert response.status_code == status.HTTP_200_OK
