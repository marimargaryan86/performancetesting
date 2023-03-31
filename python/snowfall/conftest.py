from __future__ import annotations

import asyncio
import datetime
from typing import AnyStr

import pytest
from fakeredis import aioredis as fakeredis
from motor import core, motor_asyncio
from redis import asyncio as aioredis

from snowfall import fixtures
from snowfall.project.junction.go.adapter import (
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    passenger_name_records,
    places,
    price_quotes,
    schedules,
    seat_maps,
    segments,
    trip_candidate_searches,
    trip_candidates,
    trip_searches,
    trips,
)
from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.pay.adapter import currencies
from snowfall.stdlib import h3
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.mongo import repository
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.junction.go import client

pytest.register_assert_rewrite("snowfall.stdlib.integration.starlette.testing")
pytest.register_assert_rewrite("snowfall.stdlib.testing.asserts")
stdout.configure_logger()


def _mongo_mock_configure(
    collection: motor_asyncio.AsyncIOMotorCollection,
) -> core.AgnosticCollection:
    return collection


repository._configure_collection = _mongo_mock_configure  # noqa: WPS437


@pytest.fixture
def redis_client() -> aioredis.Redis[AnyStr]:
    return fakeredis.FakeRedis()


@pytest.fixture
def decoding_redis_client() -> aioredis.Redis[AnyStr]:
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def currencies_client() -> currencies.Client:
    return currencies.DictClient(fixtures.get_currencies())


@pytest.fixture
def legs_client() -> legs.Client:
    return legs.DictClient(fixtures.get_legs())


@pytest.fixture
def locations_client() -> locations.Client:
    return locations.DictClient(fixtures.get_locations())


@pytest.fixture
def places_client() -> places.Client:
    return places.DictClient(fixtures.get_places())


@pytest.fixture
def passenger_name_records_client() -> passenger_name_records.Client:
    return passenger_name_records.DictClient(fixtures.get_passenger_name_records())


@pytest.fixture
def seat_maps_client() -> seat_maps.Client:
    return seat_maps.DictClient(fixtures.get_seat_maps())


@pytest.fixture
def schedules_client() -> schedules.Client:
    return schedules.DictClient(fixtures.get_schedules())


@pytest.fixture
def segments_client() -> segments.Client:
    return segments.DictClient(fixtures.get_segments())


@pytest.fixture
def trips_client() -> trips.Client:
    return trips.DictClient(fixtures.get_trips())


@pytest.fixture
def trip_searches_client() -> trip_searches.Client:
    return trip_searches.DictClient()


@pytest.fixture
def trip_candidate_searches_client() -> trip_candidate_searches.Client:
    return trip_candidate_searches.DictClient()


@pytest.fixture
def trip_candidates_client() -> trip_candidates.Client:
    return trip_candidates.DictClient()


@pytest.fixture
def offers_client() -> offers.Client:
    return offers.DictClient(fixtures.OFFER_SEARCHES[0], fixtures.get_offers())


@pytest.fixture
def offer_searches_client() -> offer_searches.Client:
    return offer_searches.DictClient(fixtures.get_offer_searches())


@pytest.fixture
def price_quotes_client() -> price_quotes.Client:
    return price_quotes.DictClient(fixtures.get_price_quotes())


@pytest.fixture
def orders_client() -> orders.Client:
    return orders.DictClient(fixtures.get_journeys())


@pytest.fixture
def offer_search() -> offer_models_pb2.OfferSearch:
    return offer_models_pb2.OfferSearch(
        trip=offer_models_pb2.TripOfferSearch(),
    )


@pytest.fixture
def junction_client() -> client.Client:
    return client.Client("", "")


@pytest.fixture
async def trip_search_request(
    places_client: places.Client,
) -> trip_searches.TripSearchRequest:
    (origin, destination) = await asyncio.gather(
        places_client.get(fixtures.PLACES[0]),
        places_client.get(fixtures.PLACES[1]),
    )

    return trip_searches.TripSearchRequest(
        origins=[
            models_pb2.Point(
                ref=origin.location.id,
                name=origin.location.name,
                coordinates=models_pb2.Coordinates(
                    latitude=origin.location.coordinates.latitude,
                    longitude=origin.location.coordinates.longitude,
                ),
                time_zone=origin.location.time_zone,
            ),
        ],
        destinations=[
            models_pb2.Point(
                ref=destination.location.id,
                name=destination.location.name,
                coordinates=models_pb2.Coordinates(
                    latitude=destination.location.coordinates.latitude,
                    longitude=destination.location.coordinates.longitude,
                ),
                time_zone=destination.location.time_zone,
            ),
        ],
        departure_after=datetime.datetime.now(datetime.timezone.utc),
        maximum_connections=None,
        allowed_segment_types=[],
    )


@pytest.fixture
async def trip_candidate_search_request() -> (
    trip_candidate_searches.TripCandidateSearchRequest
):
    return trip_candidate_searches.TripCandidateSearchRequest(
        criteria=[],
        passengers=[],
        allowed_segment_types=[],
    )


@pytest.fixture
def h3_mapping_repository() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    return h3.H3MappingRepository(
        mapping=fixtures.H3_LOCATIONS,
        resolution=8,
    )
