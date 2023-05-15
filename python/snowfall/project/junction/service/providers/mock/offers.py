import dataclasses
import datetime
from collections.abc import AsyncIterator
from typing import Sequence

import faker
import more_itertools
from google.protobuf import message

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1alpha import models_pb2 as common_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf

BRAND_NAME = "BASIC"
_TTL = datetime.timedelta(minutes=45)


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


async def offer_group_generator(
    search: Criteria,
) -> AsyncIterator[offers_pb2.OfferGroup]:
    fake = faker.Faker()
    expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + _TTL
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
            operator=fake.lexify(text="??").upper(),
            vendor=fake.lexify(text="??").upper(),
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
                id=string.uuid(),  # TODO: cache this so it can be reused in pricing
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
                price=money.from_string(
                    string_amount=fake.numerify(text="%#"),
                    currency=money.Currency("EUR"),
                ).protobuf(),
                brand_name=BRAND_NAME,
            ),
        ],
        segments=offer_segments,
    )


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
