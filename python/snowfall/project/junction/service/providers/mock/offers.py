import dataclasses
import datetime
import random
import types
from collections.abc import AsyncIterator, Callable, Sequence
from typing import Any

import faker
import more_itertools
from google.protobuf import message, timestamp_pb2

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.service.providers.mock import cache
from snowfall.project.junction.service.providers.mock.constant import PROVIDER_ID
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf

BRAND_NAME = "BASIC"
_SECONDS_IN_HR = 3600
_TIMESTAMP_PB_FACTOR = 1e9
_SNOWFALL_OPERATORS = (
    (common_pb2.Schedule.TYPE_AIR, "Icey Airways"),
    (common_pb2.Schedule.TYPE_RAIL, "Glacier Rail"),
    (common_pb2.Schedule.TYPE_FERRY, "Frosty Ferries"),
    (common_pb2.Schedule.TYPE_BUS, "Snowdrift Coaches"),
)

_SNOWFALL_VENDORS = (
    (common_pb2.Schedule.TYPE_AIR, "Snowfall Airlines"),
    (common_pb2.Schedule.TYPE_RAIL, "Snowfall Railways"),
    (common_pb2.Schedule.TYPE_FERRY, "Snowfall Ferries"),
    (common_pb2.Schedule.TYPE_BUS, "Snowfall Coaches"),
)

_AVERAGE_COSTS = types.MappingProxyType(
    {
        common_pb2.Schedule.TYPE_AIR: {
            "SHORT": (100, 300),
            "MED": (250, 500),
            "LONG": (900, 1500),
        },
        common_pb2.Schedule.TYPE_RAIL: {
            "SHORT": (30, 80),
            "MED": (50, 150),
            "LONG": (100, 300),
        },
        common_pb2.Schedule.TYPE_FERRY: {
            "SHORT": (50, 100),
            "MED": (60, 150),
            "LONG": (100, 250),
        },
        common_pb2.Schedule.TYPE_BUS: {
            "SHORT": (15, 50),
            "MED": (40, 90),
            "LONG": (80, 150),
        },
    },
)

_AVERAGE_TIMES = types.MappingProxyType(
    {
        common_pb2.Schedule.TYPE_AIR: {
            "SHORT": (0, 3),
            "MED": (3, 8),
            "LONG": (8, 999),
        },
        common_pb2.Schedule.TYPE_RAIL: {
            "SHORT": (0, 2),
            "MED": (2, 8),
            "LONG": (8, 999),
        },
        common_pb2.Schedule.TYPE_FERRY: {
            "SHORT": (0, 2),
            "MED": (2, 6),
            "LONG": (6, 999),
        },
        common_pb2.Schedule.TYPE_BUS: {
            "SHORT": (0, 4),
            "MED": (4, 10),
            "LONG": (10, 999),
        },
    },
)


def _calculate_reasonable_price(  # noqa: WPS210
    travel_type: common_pb2.Schedule.Type.ValueType,
    departure: timestamp_pb2.Timestamp,
    arrival: timestamp_pb2.Timestamp,
) -> int | None:
    start_seconds = departure.seconds + departure.nanos / _TIMESTAMP_PB_FACTOR
    end_seconds = arrival.seconds + arrival.nanos / _TIMESTAMP_PB_FACTOR
    travel_time_hours = (end_seconds - start_seconds) / _SECONDS_IN_HR

    if travel_type in _AVERAGE_COSTS and travel_type in _AVERAGE_TIMES:
        for time_range, cost_range in _AVERAGE_TIMES[travel_type].items():
            min_time, max_time = cost_range
            if min_time <= travel_time_hours < max_time:
                min_cost, max_cost = map(int, _AVERAGE_COSTS[travel_type][time_range])
                return random.randint(min_cost, max_cost)  # noqa: S311
        return None
    return None


@dataclasses.dataclass(frozen=True)
class Criteria(message.Message):
    segments: Sequence[common_pb2.Segment]

    def __str__(self) -> str:
        return "segments={0}".format(str(self.segments))


def criteria_task_generator(search: offers_pb2.TripOfferSearch) -> list[Criteria]:
    return [criteria for trip in search.trips for criteria in _trip_to_criteria(trip)]


def criteria_generator(search: Criteria) -> Criteria:
    return search


def cache_key(search: Criteria) -> str:
    return string.uuid()


class Generator(object):
    def __init__(
        self,
        reasonable_results: bool,  # noqa: FBT001
        option_cache: cache.OptionCache,
        ttl: datetime.timedelta,
    ):
        self._reasonable_results = reasonable_results
        self._cache = option_cache
        self._ttl = ttl

    async def generate(  # noqa: WPS210
        self,
        search: Criteria,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        fake = faker.Faker()
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        operator = fake.lexify(text="??").upper()
        vendor = fake.lexify(text="??").upper()
        price = money.from_string(
            string_amount=(fake.numerify(text="%#")),
            currency=money.Currency("EUR"),
        )
        if self._reasonable_results:
            segments = search.segments
            departure = segments[0].legs[0].departure_at
            arrival = segments[-1].legs[-1].arrival_at
            travel_type = segments[0].legs[0].type
            reasonable_price = _calculate_reasonable_price(
                travel_type,
                departure,
                arrival,
            )
            operator = _get_name_from_type(travel_type, _SNOWFALL_OPERATORS)
            vendor = _get_name_from_type(
                travel_type,
                _SNOWFALL_VENDORS,
            )
            price = money.from_string(
                string_amount=(str(reasonable_price)),
                currency=money.Currency("EUR"),
            )
        offer_segments = [
            offers_pb2.OfferSegment(
                id=string.uuid(),
                legs=[
                    offers_pb2.OfferSegmentLeg(
                        id=string.uuid(),
                        origin=leg.origin,
                        destination=leg.destination,
                        departure_at=leg.departure_at,
                        arrival_at=leg.arrival_at,
                    )
                    for leg in segment.legs
                ],
                operator=operator,
                vendor=vendor,
                vehicle=offers_pb2.Vehicle(
                    number=fake.numerify(text="%##"),
                ),
                type=more_itertools.first(segment.legs).type,
            )
            for segment in search.segments
        ]

        yield offers_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[
                offers_pb2.Offer(
                    id=await self._cache.store(
                        cache.MockDetails(
                            amount=price.amount,
                            currency=price.currency.code,
                        ),
                        expires_at=expires_at,
                    ),
                    segment_details=[
                        offers_pb2.OfferSegmentDetails(
                            id=string.uuid(),
                            offer_segment_id=offer_segment.id,
                            cabin_class=common_pb2.CabinClass(
                                type=common_pb2.CabinClass.TYPE_ECONOMY,
                                marketing_name="Economy",
                            ),
                        )
                        for offer_segment in offer_segments
                    ],
                    price=price.protobuf(),
                    brand_name=BRAND_NAME,
                ),
            ],
            segments=offer_segments,
            provider_id=str(PROVIDER_ID),
        )


def offer_group_generator(
    generator: Generator,
) -> Callable[[Criteria], AsyncIterator[offers_pb2.OfferGroup]]:
    def wrapper(
        search_criteria: Criteria,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        return generator.generate(search_criteria)

    return wrapper


def _trip_to_criteria(
    trip: common_pb2.Trip,
) -> list[Criteria]:
    criteria: list[Criteria] = []
    segments: list[common_pb2.Segment] = []
    last_type = None

    for segment in trip.segments:
        first_leg = more_itertools.first(segment.legs)

        if segments and first_leg.type != last_type:
            criteria.append(Criteria(segments=segments))
            segments.clear()

        segments.append(segment)
        last_type = first_leg.type

    if segments:
        criteria.append(Criteria(segments=segments))

    return criteria


def _get_name_from_type(
    travel_type: common_pb2.Schedule.Type.ValueType,
    snowfall_mapping: Any,
) -> str | None:
    for schedule_type, operator_name in snowfall_mapping:
        if schedule_type == travel_type:
            return operator_name
    return None
