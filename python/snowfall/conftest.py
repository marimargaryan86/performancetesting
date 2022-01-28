import datetime
import uuid

import pytest

from snowfall.adapter import places, trip_searches, trips
from snowfall.logging import stdout

# todo: would be nice with some "well-known" test data for places etc. in a package.
PLACE_NOT_FOUND = "f55b0ec5-7c87-4c35-86f4-1417a5f50e89"
PLACES = (
    {"id": "f236a92c-4cfa-468e-85ef-431d25dcd925"},
    {"id": "488a836d-ec22-439b-a9d8-3c4c386a731e"},
)

stdout.configure_logger()


@pytest.fixture
def places_client() -> places.Client:
    return places.DictClient(PLACES)


@pytest.fixture
def trips_client() -> trips.Client:
    return trips.DictClient()


@pytest.fixture
def trip_searches_client(trips_client: trips.DictClient) -> trip_searches.Client:
    return trip_searches.DictClient(trips_client=trips_client)


@pytest.fixture
async def trip_search_request(
    places_client: places.Client,
) -> trip_searches.TripSearchRequest:
    return trip_searches.TripSearchRequest(
        origin=await places_client.get(
            uuid.UUID(PLACES[0]["id"]),
        ),
        destination=await places_client.get(
            uuid.UUID(PLACES[1]["id"]),
        ),
        departure_after=datetime.datetime.now(datetime.timezone.utc),
    )
