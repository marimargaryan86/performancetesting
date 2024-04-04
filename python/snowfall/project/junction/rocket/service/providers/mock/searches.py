import dataclasses
import datetime
from collections.abc import AsyncIterator, Callable

import faker
from google.protobuf import message

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.rocket.service.providers.mock import cache
from snowfall.project.junction.rocket.service.providers.mock.constant import PROVIDER_ID
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf

BRAND_NAME = "BASIC"
_SECONDS_IN_HR = 3600
_TIMESTAMP_PB_FACTOR = 1e9


@dataclasses.dataclass(frozen=True)
class CarRentalCriteria(message.Message):
    search_id: str
    origin: legacy_go_pb2.Point
    destination: legacy_go_pb2.Point
    pickup_datetime: datetime.datetime
    return_datetime: datetime.datetime
    driver_age: int


def cache_key(search: CarRentalCriteria) -> str:
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
        search: CarRentalCriteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        fake = faker.Faker()
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price = money.from_string(
            string_amount=(fake.numerify(text="%#")),
            currency=money.Currency("EUR"),
        )

        result_details = [
            models_pb2.ResultDetail(
                id=string.uuid(),
                car_rental=models_pb2.CarRentalResultDetail(
                    origin=search.origin,
                    destination=search.destination,
                    image_url="www.example.com/image",
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
                ),
            ),
        ]

        conditional_price = models_pb2.ConditionalPrice(
            price=price.protobuf(),
            description="This is a conditional price",
            included_in_total=False,
        )

        yield models_pb2.SearchResult(
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


def search_result_generator(
    generator: Generator,
) -> Callable[[CarRentalCriteria], AsyncIterator[models_pb2.SearchResult]]:
    def wrapper(
        search_criteria: CarRentalCriteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        return generator.generate(search_criteria)

    return wrapper


def search_criteria_task_generator(
    search: models_pb2.Search,
) -> list[CarRentalCriteria]:
    if search.HasField("car_rental"):
        return car_rental_task_generator(search)
    return []


def car_rental_task_generator(
    search: models_pb2.Search,
) -> list[CarRentalCriteria]:
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
