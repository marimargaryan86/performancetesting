import datetime
import uuid
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Mapping, Sequence, Tuple

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import airports, cache, models
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.ask2go.models import booking, offers, price


class OfferTransformer(object):
    def __init__(
        self,
        airport_repository: airports.AirportRepository,
        offer_cache: cache.OfferCache,
        offer_ttl: datetime.timedelta,
    ):
        self._airports = airport_repository
        self._cache = offer_cache
        self._ttl = offer_ttl

    async def offer_prices_to_offer_groups(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_prices: AsyncIterator[price.OfferPriceResponse],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        async for offer_price in offer_prices:
            yield await self._offer_price_to_offer_group(search_task, offer_price)

    async def _offer_price_to_offer_group(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_price: price.OfferPriceResponse,
    ) -> offers_pb2.OfferGroup:
        segment = more_itertools.first(
            more_itertools.first(offer_price.itinerary.trips).segments,
        )
        search_segment = more_itertools.first(search_task.segments)
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl
        offer_segment = self._segment_to_proto(
            segment=segment,
            search_segment=search_segment,
            grouped_rules=self._group_rules_by_origin_destination(
                offer_price.fare_rules,
            ),
        )
        amount = money.from_string(
            offer_price.itinerary.pricing_information.base.total_cost,
            money.Currency(offer_price.itinerary.pricing_information.base.currency),
        )

        return offers_pb2.OfferGroup(
            id=str(uuid.uuid4()),
            offer_search_id=search_task.offer_search_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[
                offers_pb2.Offer(
                    id=await self._cache.store(
                        cache.OfferDetails(
                            pricing_id=offer_price.id,
                            transaction_id=offer_price.transaction_id,
                        ),
                        expires_at=expires_at,
                    ),
                    segment_details=[
                        offers_pb2.OfferSegmentDetails(
                            id=str(uuid.uuid4()),
                            offer_segment_id=offer_segment.id,
                            cabin_class=models_pb2.CabinClass(
                                type=models.cabin_to_proto(segment.cabin),
                                marketing_name=segment.cabin or "",
                            ),
                        ),
                    ],
                    price=models_pb2.Price(
                        amount=amount.amount,
                        currency=amount.currency.code,
                    ),
                ),
            ],
            segments=[offer_segment],
        )

    def _segment_to_proto(
        self,
        segment: offers.TripSegment,
        search_segment: models_pb2.Segment,
        grouped_rules: Mapping[Tuple[str, str], Sequence[booking.FareRule]],
    ) -> offers_pb2.OfferSegment:
        origin = self._airports.get_by_iata(segment.origin.airport_code)
        destination = self._airports.get_by_iata(segment.destination.airport_code)

        return offers_pb2.OfferSegment(
            id=str(uuid.uuid4()),
            segment_id=search_segment.id,
            legs=[
                offers_pb2.OfferSegmentLeg(
                    id=search_segment.legs[0].id,
                    origin=models_pb2.Point(
                        ref=origin.iata,
                        name=origin.airport_name or "",
                        coordinates=models_pb2.Coordinates(
                            latitude=origin.latitude,
                            longitude=origin.longitude,
                        ),
                        time_zone=origin.timezone.key,
                    ),
                    destination=models_pb2.Point(
                        ref=destination.iata,
                        name=destination.airport_name or "",
                        coordinates=models_pb2.Coordinates(
                            latitude=destination.latitude,
                            longitude=destination.longitude,
                        ),
                        time_zone=destination.timezone.key,
                    ),
                    departure_at=protobuf.datetime_to_protobuf(
                        segment.departure.date_time.replace(
                            tzinfo=origin.timezone,
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        segment.arrival.date_time.replace(
                            tzinfo=destination.timezone,
                        ),
                    ),
                    rules=[
                        offers_pb2.Rule(
                            body=rule.text,
                            title=rule.title,
                        )
                        for rule in grouped_rules[
                            (
                                segment.origin.airport_code,
                                segment.destination.airport_code,
                            )
                        ]
                    ],
                ),
            ],
            vehicle=offers_pb2.Vehicle(
                equipment=segment.aircraft.equipment,
                number=segment.aircraft.flight_number,
            ),
            operator=segment.operating_carrier.code,
            vendor=segment.marketing_carrier.code,
            terminal=segment.origin_terminal or "",
            type=models_pb2.Schedule.TYPE_AIR,
        )

    def _group_rules_by_origin_destination(
        self,
        fare_rules: Sequence[booking.FareRules],
    ) -> Mapping[Tuple[str, str], Sequence[booking.FareRule]]:
        grouped_rules = {}

        for fare_rule in fare_rules:
            with suppress(IndexError):
                fare_rule.fare_rule.pop(0)

            grouped_rules[
                (fare_rule.origin, fare_rule.destination)
            ] = fare_rule.fare_rule

        return grouped_rules
