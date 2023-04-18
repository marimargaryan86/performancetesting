import datetime
from typing import Any, Mapping

import freezegun
import httpx
import pytest
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import trip_searches


class TestTrips(object):
    async def test_missing_trip_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_trip_is_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/{id}".format(id=fixtures.TRIPS[0]),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_get_trip_segments(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/{id}/segments".format(id=fixtures.TRIPS[0]),
        )
        assert response.status_code == status.HTTP_200_OK


class TestTripSearches(object):
    async def test_malformed_trip_search_post_returns_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/trips/searches",
            json={"foo": "bar"},
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_trip_search_post_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
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
        response = await client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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
        query: Mapping[str, Any],
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/trips/searches",
            json=query,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_past_departure_date_returns_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "attributes": {
                    "departureAfter": "1957-04-30T08:34:00.826Z",
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
        response = await client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_invalid_segment_types(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "attributes": {
                    "departureAfter": datetime.datetime.now(
                        tz=datetime.timezone.utc,
                    ).isoformat(timespec="seconds"),
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
                    "allowedSegmentTypes": {
                        "data": [
                            {
                                "id": "foobar",
                                "type": "leg-types",
                            },
                        ],
                    },
                },
                "type": "trip-searches",
            },
        }
        response = await client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @freezegun.freeze_time("2022-04-30T08:30:30.826Z")
    async def test_departure_date_without_tz_returns_unprocessable_entity(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "attributes": {
                    "departureAfter": "2022-04-30T08:34:00.985933",
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
        response = await client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @freezegun.freeze_time("2022-04-30T08:34:30.826Z")
    async def test_trip_search_post_returns_resource(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "attributes": {
                    "departureAfter": "2022-04-30T08:34:00.826Z",
                    "arrivalBefore": "2022-08-17T08:12:02.822Z",
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
                    "allowedSegmentTypes": {
                        "data": [
                            {
                                "id": "air",
                                "type": "leg-types",
                            },
                        ],
                    },
                },
                "type": "trip-searches",
            },
        }
        response = await client.post(
            "/trips/searches",
            json=request,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_created_trip_search_can_be_retrieved(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: httpx.AsyncClient,
    ) -> None:
        trip_search = await trip_searches_client.create(trip_search_request)
        response = await client.get(
            "/trips/searches/{id}".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_created_trip_search_unauthorized(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: httpx.AsyncClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
        trip_search = await trip_searches_client.create(trip_search_request)
        response = await client.get(
            "/trips/searches/{id}".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_missing_trip_search_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/searches/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_trips_unauthorized(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: httpx.AsyncClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
        trip_search = await trip_searches_client.create(trip_search_request)
        response = await client.get(
            "/trips/searches/{id}/trips".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_missing_trips_by_search_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/searches/{id}/trips".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_malformed_uuid_returns_bad_request(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/trips/searches/{id}/trips".format(id="foo"),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_trips_are_found(
        self,
        trip_searches_client: trip_searches.Client,
        trip_search_request: trip_searches.TripSearchRequest,
        client: httpx.AsyncClient,
    ) -> None:
        trip_search = await trip_searches_client.create(trip_search_request)
        response = await client.get(
            "/trips/searches/{id}/trips".format(id=trip_search.id),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]
        assert response.json()["links"]["next"] != ""
