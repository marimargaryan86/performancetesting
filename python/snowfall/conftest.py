import asyncio
import datetime
from typing import Sequence

import aioredis
import aiosmtplib
import pytest
from fakeredis import aioredis as fakeredis
from motor import core, motor_asyncio

from snowfall import fixtures
from snowfall.project.junction.adapter import (
    currencies,
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    passenger_name_records,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.project.junction.service.mobile_api import smtp
from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.stdlib import h3
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.mongo import repository
from snowfall.stdlib.persistence.mongo.normalizers import TimestampNormalizer
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.junction import client

pytest.register_assert_rewrite("snowfall.stdlib.integration.starlette.routes.testing")
pytest.register_assert_rewrite("snowfall.stdlib.testing.asserts")
stdout.configure_logger()


def _mongo_mock_configure(
    collection: motor_asyncio.AsyncIOMotorCollection,
) -> core.AgnosticCollection:
    return collection


def _mock_denormalize_value(  # type: ignore[no-untyped-def]
    self,  # noqa: ANN001
    normalized_value: datetime.datetime,
) -> str:
    if not normalized_value.tzinfo:
        normalized_value = normalized_value.replace(tzinfo=datetime.timezone.utc)

    return normalized_value.isoformat()


repository._configure_collection = _mongo_mock_configure  # noqa: WPS437
TimestampNormalizer._denormalize_value = (  # type: ignore[assignment] # noqa: WPS437
    _mock_denormalize_value
)


@pytest.fixture
def smtp_client() -> smtp.EmailClient:
    return smtp.EmailClient(aiosmtplib.SMTP())


@pytest.fixture
def redis_client() -> aioredis.Redis:
    return fakeredis.FakeRedis()


@pytest.fixture
def decoding_redis_client() -> aioredis.Redis:
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
def offers_client() -> offers.Client:
    return offers.DictClient(fixtures.get_offers())


@pytest.fixture
def offer_searches_client() -> offer_searches.Client:
    return offer_searches.DictClient(fixtures.get_offer_searches())


@pytest.fixture
def orders_client() -> orders.Client:
    return orders.DictClient(fixtures.get_orders())


@pytest.fixture
def offer_search() -> offer_models_pb2.OfferSearch:
    return offer_models_pb2.OfferSearch(
        trip=offer_models_pb2.TripOfferSearch(),
    )


@pytest.fixture
def junction_client() -> client.JunctionClient:
    return client.JunctionClient("", "")


@pytest.fixture
async def trip_search_request(
    places_client: places.Client,
) -> trip_searches.TripSearchRequest:
    (origin, destination) = await asyncio.gather(
        places_client.get(fixtures.PLACES[0]),
        places_client.get(fixtures.PLACES[1]),
    )

    return trip_searches.TripSearchRequest(
        origin=models_pb2.Point(
            ref=origin.location.id,
            name=origin.location.name,
            coordinates=models_pb2.Coordinates(
                latitude=origin.location.coordinates.latitude,
                longitude=origin.location.coordinates.longitude,
            ),
            time_zone=origin.location.time_zone,
        ),
        destination=models_pb2.Point(
            ref=destination.location.id,
            name=destination.location.name,
            coordinates=models_pb2.Coordinates(
                latitude=destination.location.coordinates.latitude,
                longitude=destination.location.coordinates.longitude,
            ),
            time_zone=destination.location.time_zone,
        ),
        departure_after=datetime.datetime.now(datetime.timezone.utc),
    )


@pytest.fixture
def h3_mapping_repository(
    h3_mapping: Sequence[h3.CoordinatesItem[fixtures.H3LocationTestModel]],
) -> h3.H3MappingRepository[fixtures.H3LocationTestModel]:
    return h3.H3MappingRepository(
        mapping=h3_mapping,
        resolution=8,
    )


@pytest.fixture
def h3_mapping() -> list[h3.CoordinatesItem[fixtures.H3LocationTestModel]]:
    return [
        h3.CoordinatesItem[fixtures.H3LocationTestModel](
            latitude=location.latitude,
            longitude=location.longitude,
            mapped_value=location,
        )
        for location in fixtures.H3_LOCATIONS
    ]
