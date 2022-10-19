import datetime
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Mapping, Sequence, Tuple

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import airports, cache, models
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.ask2go.models import booking, offers, price

_BrandedOffersType = Tuple[Sequence[str], Sequence[price.OfferPriceResponse]]
_GroupedOfferSegment = Tuple[offers.TripSegment, offers_pb2.OfferSegment]


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
        grouped_offer_prices: AsyncIterator[_BrandedOffersType],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        async for offer_prices in grouped_offer_prices:
            yield await self._offer_prices_to_offer_group(search_task, offer_prices)

    async def _offer_prices_to_offer_group(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        branded_prices: Tuple[Sequence[str], Sequence[price.OfferPriceResponse]],
    ) -> offers_pb2.OfferGroup:
        brands = branded_prices[0]
        offer_prices = branded_prices[1]
        search_segment = more_itertools.first(search_task.segments)
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        grouped_offer_segments = [
            (
                segment,
                self._segment_to_proto(
                    segment=segment,
                    search_segment=search_segment,
                ),
            )
            for trip in offer_prices[0].itinerary.trips
            for segment in trip.segments
        ]

        return offers_pb2.OfferGroup(
            id=string.uuid(),
            offer_search_id=search_task.offer_search_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=await self._get_group_offers(
                offer_prices,
                brands,
                expires_at,
                grouped_offer_segments,
            ),
            segments=[grouped_segment[1] for grouped_segment in grouped_offer_segments],
        )

    async def _get_group_offers(
        self,
        offer_prices: Sequence[price.OfferPriceResponse],
        brands: Sequence[str],
        expires_at: datetime.datetime,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
    ) -> Sequence[offers_pb2.Offer]:
        group_offers = []
        for index, offer_price in enumerate(offer_prices):
            grouped_rules = self._group_rules_by_origin_destination(
                offer_price.fare_rules,
            )
            amount = money.from_string(
                offer_price.itinerary.pricing_information.base.total_cost,
                money.Currency(offer_price.itinerary.pricing_information.base.currency),
            )

            group_offers.append(
                offers_pb2.Offer(
                    id=await self._cache.store(
                        cache.OfferDetails(
                            pricing_id=offer_price.id,
                            transaction_id=offer_price.transaction_id,
                        ),
                        expires_at=expires_at,
                    ),
                    segment_details=self._get_segment_details(
                        grouped_trips_segments,
                        grouped_rules,
                    ),
                    price=models_pb2.Price(
                        amount=amount.amount,
                        currency=amount.currency.code,
                    ),
                    brand_name=brands[index],
                ),
            )

        return group_offers

    def _get_segment_details(
        self,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
        grouped_rules: Mapping[Tuple[str, str], Sequence[booking.FareRule]],
    ) -> Sequence[offers_pb2.OfferSegmentDetails]:
        segment_details = []
        for grouped_segment in grouped_trips_segments:
            segment_details.append(
                offers_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=grouped_segment[1].id,
                    cabin_class=models_pb2.CabinClass(
                        type=models.cabin_to_proto(grouped_segment[0].cabin),
                        marketing_name=grouped_segment[0].cabin or "",
                    ),
                    rules=[
                        offers_pb2.SegmentRule(
                            body=rule.text,
                            title=rule.title,
                        )
                        for rule in grouped_rules[
                            (
                                grouped_segment[0].origin.airport_code,
                                grouped_segment[0].destination.airport_code,
                            )
                        ]
                    ],
                ),
            )

        return segment_details

    def _segment_to_proto(
        self,
        segment: offers.TripSegment,
        search_segment: models_pb2.Segment,
    ) -> offers_pb2.OfferSegment:
        origin = self._airports.get_by_iata(segment.origin.airport_code)
        destination = self._airports.get_by_iata(segment.destination.airport_code)

        return offers_pb2.OfferSegment(
            id=string.uuid(),
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
