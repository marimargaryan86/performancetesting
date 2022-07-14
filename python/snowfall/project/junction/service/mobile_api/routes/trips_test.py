import asyncio

import pytest_httpx
from starlette import status, testclient

from snowfall.project.junction.service.mobile_api import conftest, repository
from snowfall.project.junction.service.mobile_api.tasks import trips


class TestTrips(object):
    async def test_trip_search_created(
        self,
        authenticated_http_client: testclient.TestClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        trip_searches_repository: repository.TripSearchesRepository,
    ) -> None:
        httpx_mock.add_response(
            **conftest.load_response_fixture("POST_TRIPS_SEARCHES.json"),
        )
        httpx_mock.add_response(
            **conftest.load_response_fixture("GET_TRIPS_SEARCHES_{ID}_TRIPS.json"),
        )
        httpx_mock.add_response(
            **conftest.load_response_fixture("GET_SEGMENTS_{ID}_LEGS.json"),
        )

        response = authenticated_http_client.post(
            "/trips/searches",
            json={
                "data": {
                    "type": "trip-searches",
                    "attributes": {
                        "departureAfter": "2022-06-18T05:00:00.826Z",
                        "arrivalBefore": "2022-06-22T09:17:00.126Z",
                        "passengers": {"adults": 0, "children": 0, "infants": 0},
                        "cabinClass": "economy",
                        "roundTrip": True,
                    },
                    "relationships": {
                        "origin": {
                            "data": {
                                "id": "049c6945-de3c-5eca-a578-aec753f064c3",
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": "0b2a62b3-1050-5c56-b447-b3fc89138356",
                                "type": "places",
                            },
                        },
                        "legTypes": {"data": []},
                    },
                },
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert (
            await trip_searches_repository.find_by_id(
                response.json()["data"]["id"],
                "id",
            )
            is not None
        )
        await asyncio.sleep(trips._TRIPS_POLLING_INTERVAL + 0.5)  # noqa: WPS437
        stored_trip_search = await trip_searches_repository.find_by_id(
            response.json()["data"]["id"],
            "id",
        )

        assert stored_trip_search
        relationships = stored_trip_search.get("relationships")
        assert relationships
        assert relationships.get("trips")
