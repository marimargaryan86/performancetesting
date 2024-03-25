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

BRAND_NAME = "BASIC"
_SECONDS_IN_HR = 3600
_TIMESTAMP_PB_FACTOR = 1e9


@dataclasses.dataclass(frozen=True)
class Criteria(message.Message):
    origin: str
    destination: str
    passenger_dobs: Sequence[datetime.date]
    outbound_departure_datetime: datetime.datetime
    inbound_departure_datetime: datetime.datetime
    outbound_search_result_id: str | None = None


def cache_key(search: Criteria) -> str:
    return string.uuid()


class Generator(object):
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

        result_details = [
            models_pb2.ResultDetail(
                id=string.uuid(),
                mock=models_pb2.MockResultDetail(
                    origin=legacy_go_pb2.Point(
                        name=search.origin,
                    ),
                    destination=legacy_go_pb2.Point(
                        name=search.destination,
                    ),
                    outbound_segment=True,
                    segment_sequence=1,
                ),
            ),
        ]
        if search.outbound_search_result_id:
            result_details.append(
                models_pb2.ResultDetail(
                    id=string.uuid(),
                    mock=models_pb2.MockResultDetail(
                        origin=legacy_go_pb2.Point(
                            name=search.destination,
                        ),
                        destination=legacy_go_pb2.Point(
                            name=search.origin,
                        ),
                        outbound_segment=False,
                        segment_sequence=2,
                    ),
                ),
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


def search_criteria_task_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    return [
        Criteria(
            origin=search.mock.origin.name,
            destination=search.mock.destination.name,
            passenger_dobs=[
                protobuf.protobuf_to_date(search.mock.passengers[0].date_of_birth),
            ],
            outbound_departure_datetime=protobuf.protobuf_to_datetime(
                search.mock.departure_date,
            ),
            inbound_departure_datetime=protobuf.protobuf_to_datetime(
                search.mock.return_date,
            ),
            outbound_search_result_id=(
                search.mock.outbound_search_result_id
                if search.mock.outbound_search_result_id
                else None
            ),
        ),
    ]
