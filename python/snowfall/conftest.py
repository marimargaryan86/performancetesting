import datetime

import pytest

from snowfall import fixtures
from snowfall.adapter import places, trip_searches
from snowfall.logging import stdout

stdout.configure_logger()


@pytest.fixture
def places_client() -> places.Client:
    return places.DictClient(fixtures.get_places())


@pytest.fixture
def trip_searches_client() -> trip_searches.Client:
    return trip_searches.DictClient()


@pytest.fixture
async def trip_search_request(
    places_client: places.Client,
) -> trip_searches.TripSearchRequest:
    return trip_searches.TripSearchRequest(
        origin=await places_client.get(
            fixtures.PLACES[0],
        ),
        destination=await places_client.get(
            fixtures.PLACES[1],
        ),
        departure_after=datetime.datetime.now(datetime.timezone.utc),
    )
