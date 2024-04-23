import dataclasses
import datetime
from collections.abc import AsyncIterator, Callable, Sequence

import faker
from google.protobuf import message

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.rocket.service.providers.mock import cache
from snowfall.project.junction.rocket.service.providers.mock.constant import PROVIDER_ID
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

BRAND_NAME = "BASIC"
_SECONDS_IN_HR = 3600
_TIMESTAMP_PB_FACTOR = 1e9


class Criteria(message.Message):
    """Base Criteria class."""


@dataclasses.dataclass(frozen=True)
class RailPlace:
    id: str
    name: str
    latitude: float
    longitude: float
    time_zone: str


@dataclasses.dataclass(frozen=True)
class RailCriteria(Criteria):
    search_id: str
    origin: RailPlace
    destination: RailPlace
    passenger_dobs: Sequence[datetime.date]
    trip_sequence: int
    departure_datetime: datetime.datetime
    return_datetime: datetime.datetime | None = None
    outbound_offer_id: str | None = None


@dataclasses.dataclass(frozen=True)
class CarRentalCriteria(Criteria):
    search_id: str
    origin: legacy_go_pb2.Point
    destination: legacy_go_pb2.Point
    pickup_datetime: datetime.datetime
    return_datetime: datetime.datetime
    driver_age: int


def cache_key(search: Criteria) -> str:
    return string.uuid()


class Generator:
    def __init__(
        self,
        search_result_cache: cache.SearchResultCache,
        ttl: datetime.timedelta,
    ):
        self._cache = search_result_cache
        self._ttl = ttl

    async def generate(
        self,
        search: Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        fake = faker.Faker()
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price = money.from_string(
            string_amount=(fake.numerify(text="%#")),
            currency=money.Currency("EUR"),
        )
        if isinstance(search, CarRentalCriteria):
            yield await self._generate_car_rental_results(search, expires_at, price)
        elif isinstance(search, RailCriteria):
            yield await self._generate_rail_results(search, expires_at, price)

    async def _generate_car_rental_results(
        self,
        search: CarRentalCriteria,
        expires_at: datetime.datetime,
        price: money.Money,
    ) -> models_pb2.SearchResult:
        result_details = [
            models_pb2.ResultDetail(
                id=string.uuid(),
                car_rental=models_pb2.CarRentalResultDetail(
                    origin=search.origin,
                    destination=search.destination,
                    image_url="http://www.example.com/image.jpg",
                    model="ferrari",
                    seats_count=2,
                    doors_count=2,
                    transmission="manual",
                    baggage_quantity=1,
                    vehicle_type="car",
                    vendor_name="enzo",
                    vendor_code="EZ",
                    unlimited_mileage=True,
                    air_conditioner=True,
                    pickup_at=protobuf.datetime_to_protobuf_datetime(
                        search.pickup_datetime,
                    ),
                    return_at=protobuf.datetime_to_protobuf_datetime(
                        search.return_datetime,
                    ),
                ),
            ),
        ]

        conditional_price = models_pb2.ConditionalPrice(
            price=price.protobuf(),
            description="This is a conditional price",
            included_in_total=False,
        )

        return models_pb2.SearchResult(
            id=string.uuid(),
            provider_id=str(PROVIDER_ID),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[
                models_pb2.Offer(
                    id=await self._cache.store(
                        cache.MockDetails(
                            amount=price.amount,
                            currency=price.currency.code,
                        ),
                        expires_at=expires_at,
                    ),
                    price=price.protobuf(),
                    car_rental=models_pb2.CarRentalOffer(
                        conditional_prices=[conditional_price],
                    ),
                ),
            ],
            result_details=result_details,
        )

    async def _generate_rail_results(
        self,
        search: RailCriteria,
        expires_at: datetime.datetime,
        price: money.Money,
    ) -> models_pb2.SearchResult:
        arrival_date = search.departure_datetime + datetime.timedelta(days=1)
        result_details = [
            models_pb2.ResultDetail(
                id=string.uuid(),
                rail=models_pb2.RailResultDetail(
                    origin=legacy_go_pb2.Point(
                        ref=search.origin.id,
                        name=search.origin.name,
                        coordinates=latlng_pb2.LatLng(
                            latitude=search.origin.latitude,
                            longitude=search.origin.longitude,
                        ),
                        time_zone=search.origin.time_zone,
                    ),
                    destination=legacy_go_pb2.Point(
                        ref=search.destination.id,
                        name=search.destination.name,
                        coordinates=latlng_pb2.LatLng(
                            latitude=search.destination.latitude,
                            longitude=search.destination.longitude,
                        ),
                        time_zone=search.destination.time_zone,
                    ),
                    departure_date=protobuf.datetime_to_protobuf_datetime(
                        search.departure_datetime,
                    ),
                    arrival_date=protobuf.datetime_to_protobuf_datetime(arrival_date),
                    outbound_segment=True,
                    segment_sequence=1,
                ),
            ),
        ]

        cabin_details = [
            models_pb2.CabinDetails(
                result_id=result_detail.id,
                cabin_class=legacy_go_pb2.CabinClass(
                    type=legacy_go_pb2.CabinClass.Type.TYPE_ECONOMY,
                    marketing_name="Economy",
                ),
            )
            for result_detail in result_details
        ]

        return models_pb2.SearchResult(
            id=string.uuid(),
            search_id=search.search_id,
            provider_id=str(PROVIDER_ID),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[
                models_pb2.Offer(
                    id=await self._cache.store(
                        cache.MockDetails(
                            amount=price.amount,
                            currency=price.currency.code,
                        ),
                        expires_at=expires_at,
                    ),
                    price=price.protobuf(),
                    rail=models_pb2.RailOffer(
                        cabin_class=cabin_details,
                    ),
                ),
            ],
            result_details=result_details,
        )


def search_result_generator(
    generator: Generator,
) -> Callable[[Criteria], AsyncIterator[models_pb2.SearchResult]]:
    def wrapper(
        search_criteria: Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        return generator.generate(search_criteria)

    return wrapper


async def search_criteria_task_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    if search.HasField("car_rental"):
        return car_rental_task_generator(search)
    if search.HasField("rail"):
        return rail_task_generator(search)
    return []


def car_rental_task_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    pickup_datetime = protobuf.protobuf_to_datetime(search.car_rental.pickup_at)
    far_future = datetime.datetime(2050, 1, 1, tzinfo=datetime.UTC)  # noqa: WPS432
    # This is for QA, to mock 0 results from a provider. E.g. too far in future
    if pickup_datetime >= far_future:
        return []
    return [
        CarRentalCriteria(
            search_id=search.id,
            origin=search.car_rental.origin,
            destination=search.car_rental.destination,
            pickup_datetime=pickup_datetime,
            return_datetime=protobuf.protobuf_to_datetime(
                search.car_rental.return_at,
            ),
            driver_age=search.car_rental.driver_age,
        ),
    ]


def rail_task_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    departure_after = protobuf.protobuf_to_datetime(search.rail.departure_after)
    far_future = datetime.datetime(2050, 1, 1, tzinfo=datetime.UTC)  # noqa: WPS432
    # This is for QA, to mock 0 results from a provider. E.g. too far in future
    if departure_after >= far_future:
        return []

    search_origin = search.rail.origin
    search_destination = search.rail.destination
    origin = RailPlace(
        id=search_origin.id,
        name=search_origin.name,
        latitude=search_origin.coordinates.latitude,
        longitude=search_origin.coordinates.longitude,
        time_zone=search_origin.time_zone,
    )
    destination = RailPlace(
        id=search_destination.id,
        name=search_destination.name,
        latitude=search_destination.coordinates.latitude,
        longitude=search_destination.coordinates.longitude,
        time_zone=search_destination.time_zone,
    )

    passenger_dobs = [
        protobuf.protobuf_to_date(passenger.date_of_birth)
        for passenger in search.rail.passengers
    ]
    return_departure_after = (
        protobuf.protobuf_to_datetime(search.rail.return_date)
        if search.rail.HasField("return_date")
        else None
    )

    return [
        RailCriteria(
            search_id=search.id,
            origin=origin,
            destination=destination,
            passenger_dobs=passenger_dobs,
            outbound_offer_id=search.rail.outbound_offer_id,
            return_datetime=return_departure_after,
            departure_datetime=departure_after,
            trip_sequence=1,
        ),
    ]
