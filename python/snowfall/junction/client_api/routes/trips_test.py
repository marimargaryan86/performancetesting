from typing import Any

import pytest
from starlette import status, testclient

from snowfall import fixtures
from snowfall.adapter import trip_searches


@pytest.mark.asyncio
class TestTrips(object):
    async def test_missing_trip_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_trip_is_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/{id}".format(id=fixtures.TRIP),
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
class TestTripSearches(object):
    async def test_malformed_trip_search_post_returns_bad_request(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/trips/searches",
            json={"foo": "bar"},
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "query",
        [
            {
                "data": {
                    "type": "trip-searches",
                    "attributes": {},
                    "relationships": {
                        "origin": {
                            "data": {
                                "id": fixtures.NOT_FOUND,
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": fixtures.PLACES[1],
                                "type": "places",
                            },
                        },
                    },
                },
            },
            {
                "data": {
                    "type": "trip-searches",
                    "attributes": {},
                    "relationships": {
                        "origin": {
                            "data": {
                                "id": fixtures.PLACES[0],
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": fixtures.NOT_FOUND,
                                "type": "places",
                            },
                        },
                    },
                },
            },
        ],
    )
    async def test_missing_place_returns_not_found(
        self,
        query: dict[str, Any],
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/trips/searches",
            json=query,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_trip_search_post_returns_resource(
        self,
        client: testclient.TestClient,
    ) -> None:
        request = {
            "data": {
                "attributes": {
                    "departureAfter": "1957-04-30T08:34:00.826Z",
                    "arrivalBefore": "1947-08-17T08:12:02.822Z",
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
                            "id": fixtures.PLACES[1],
                            "type": "places",
                        },
                    },
                },
                "type": "trip-searches",
            },
        }
        response = client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_created_trip_search_can_be_retrieved(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: testclient.TestClient,
    ) -> None:
        trip_search = await trip_searches_client.create(trip_search_request)
        response = client.get(
            "/trips/searches/{id}".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_missing_trip_search_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/searches/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_missing_trips_by_search_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/searches/{id}/trips".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_malformed_uuid_returns_bad_request(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/searches/{id}/trips".format(id="foo"),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_trips_are_found(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: testclient.TestClient,
    ) -> None:
        trip_search = await trip_searches_client.create(trip_search_request)
        response = client.get(
            "/trips/searches/{id}/trips".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]
