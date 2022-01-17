import uuid
from typing import Any

import pytest
from starlette import status, testclient

from snowfall.adapter import places
from snowfall.junction.client_api import conftest, trips


class TestHealth(object):
    def test_health_status_code(self, client: testclient.TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestPlaces(object):
    def test_unknown_place_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/places/{id}".format(id=conftest.PLACE_NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_place_is_found(self, client: testclient.TestClient) -> None:
        identifier = conftest.PLACES[0]["id"]
        response = client.get("/places/{id}".format(id=identifier))
        assert response.status_code == status.HTTP_200_OK

    def test_multiple_places_are_found(self, client: testclient.TestClient) -> None:
        response = client.get("/places")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
class TestTrips(object):
    async def test_malformed_trip_search_post_returns_bad_request(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post("/trips/searches", json={"foo": "bar"})
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
                                "id": conftest.PLACE_NOT_FOUND,
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": conftest.PLACES[1]["id"],
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
                                "id": conftest.PLACES[0]["id"],
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": conftest.PLACE_NOT_FOUND,
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
        assert response.status_code == status.HTTP_404_NOT_FOUND

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
                            "id": conftest.PLACES[0]["id"],
                            "type": "places",
                        },
                    },
                    "destination": {
                        "data": {
                            "id": conftest.PLACES[1]["id"],
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
        trip_search_repository: trips.TripSearchRepository,
        places_client: places.Client,
        client: testclient.TestClient,
    ) -> None:
        trip_search = await trip_search_repository.create(
            trips.TripSearchRequest(
                origin=await places_client.get(
                    uuid.UUID(conftest.PLACES[0]["id"]),
                ),
                destination=await places_client.get(
                    uuid.UUID(conftest.PLACES[1]["id"]),
                ),
            ),
        )
        response = client.get(
            "/trips/searches/{id}".format(id=str(trip_search.identifier)),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_missing_trip_search_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/searches/{id}".format(id=str(uuid.uuid4())),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_missing_trips_by_search_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/trips/searches/{id}/trips".format(id=str(uuid.uuid4())),
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
        trip_search_repository: trips.TripSearchRepository,
        places_client: places.Client,
        client: testclient.TestClient,
    ) -> None:
        trip_search = await trip_search_repository.create(
            trips.TripSearchRequest(
                origin=await places_client.get(
                    uuid.UUID(conftest.PLACES[0]["id"]),
                ),
                destination=await places_client.get(
                    uuid.UUID(conftest.PLACES[1]["id"]),
                ),
            ),
        )
        identifier = "9ecd1767-3f8f-4dfe-8782-5880ff89df19"
        response = client.get(
            "/trips/searches/{id}/trips".format(id=trip_search.identifier),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"][0]["id"] == identifier
