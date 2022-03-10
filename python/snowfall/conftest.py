import datetime

import pytest

from snowfall import fixtures
from snowfall.adapter import offer_searches, places, trip_searches, trips
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.logging import stdout

stdout.configure_logger()


@pytest.fixture
def places_client() -> places.Client:
    return places.DictClient(fixtures.get_places())


@pytest.fixture
def trips_client() -> trips.Client:
    return trips.DictClient(fixtures.get_trips())


@pytest.fixture
def trip_searches_client() -> trip_searches.Client:
    return trip_searches.DictClient()


@pytest.fixture
def offer_searches_client() -> offer_searches.Client:
    return offer_searches.DictClient()


@pytest.fixture
def offer_search() -> offers_pb2.OfferSearch:
    return offers_pb2.OfferSearch(
        trip=offers_pb2.TripOfferSearch(),
    )


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
