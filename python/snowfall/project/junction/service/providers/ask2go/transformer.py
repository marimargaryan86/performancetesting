import datetime
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Mapping, Optional, Sequence, Tuple

import more_itertools
from dateutil import relativedelta

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import airports, cache, models
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2, money_pb2
from snowfall.vendor.ask2go.models import booking, offers, price

_BrandedOffersType = Tuple[Sequence[str], Sequence[price.OfferPriceResponse]]
_GroupedOfferSegment = Tuple[offers.TripSegment, offers_pb2.OfferSegment]
_AdultMinAge = 18
_InfantMaxAge = 2


class OfferTransformer(object):  # noqa: WPS214
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

    async def _offer_prices_to_offer_group(  # noqa: WPS210
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        branded_prices: _BrandedOffersType,
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

        passenger_applicable_dates = self._get_passenger_type_to_applicable_dates(
            grouped_offer_segments[0][0],
        )

        return offers_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=await self._get_group_offers(
                offer_prices,
                brands,
                expires_at,
                grouped_offer_segments,
                passenger_applicable_dates,
            ),
            segments=[grouped_segment[1] for grouped_segment in grouped_offer_segments],
        )

    async def _get_group_offers(  # noqa:WPS211
        self,
        offer_prices: Sequence[price.OfferPriceResponse],
        brands: Sequence[str],
        expires_at: datetime.datetime,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
        passenger_applicable_dates: Mapping[str, offers_pb2.ApplicableTo],
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
                    penalties=[
                        offers_pb2.Penalty(
                            applicable_to=passenger_applicable_dates[
                                penalty.passenger_type.value
                            ],
                            penalty_type=models.penalty_type_to_proto(
                                information.penalty_type.value,
                            ),
                            changeable=information.changeable,
                            refundable=information.refundable,
                            applicability=models.applicability_type_to_proto(
                                information.applicability.value,
                            ),
                            price=self._get_penalty_price(information),
                        )
                        for penalty in offer_price.penalties
                        for information in penalty.information
                    ]
                    if offer_price.penalties
                    else [],
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

    def _get_penalty_price(
        self,
        information: price.PenaltyInformation,
    ) -> Optional[money_pb2.Money]:
        return (
            money.from_string(
                information.amount,
                money.Currency(information.currency),
            ).protobuf()
            if information.amount and information.currency
            else None
        )

    def _get_passenger_type_to_applicable_dates(
        self,
        first_segment: offers.TripSegment,
    ) -> Mapping[str, offers_pb2.ApplicableTo]:
        departure_date = first_segment.departure.date_time.date()

        return {
            "ADT": offers_pb2.ApplicableTo(
                date_of_birth_before=protobuf.date_to_protobuf(
                    departure_date - relativedelta.relativedelta(years=_AdultMinAge),
                ),
                date_of_birth_after=None,
            ),
            "CNN": offers_pb2.ApplicableTo(
                date_of_birth_before=protobuf.date_to_protobuf(
                    departure_date - relativedelta.relativedelta(years=_InfantMaxAge),
                ),
                date_of_birth_after=protobuf.date_to_protobuf(
                    departure_date - relativedelta.relativedelta(years=_AdultMinAge),
                ),
            ),
            "INF": offers_pb2.ApplicableTo(
                date_of_birth_before=None,
                date_of_birth_after=protobuf.date_to_protobuf(
                    departure_date - relativedelta.relativedelta(years=_InfantMaxAge),
                ),
            ),
        }
