import datetime
import itertools
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Mapping, Optional, Sequence, Tuple

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
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl
        required = set[offers_pb2.OfferGroup.Required.ValueType]()

        grouped_offer_segments = [
            (
                segment,
                self._segment_to_proto(
                    segment=segment,
                    search_segment=search_task.segments[segment_index],
                ),
            )
            for segment_index, segment in enumerate(
                itertools.chain(
                    *[trip.segments for trip in offer_prices[0].itinerary.trips],
                ),
            )
        ]

        for offer_price in offer_prices:
            required.update(self._get_offer_price_requirements(offer_price.docs))

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
            required=list(required) if required else None,
        )

    def _get_offer_price_doc_requirements(
        self,
        doc: price.OfferPriceDoc,
    ) -> set[offers_pb2.OfferGroup.Required.ValueType]:
        required = set[offers_pb2.OfferGroup.Required.ValueType]()

        if doc.required_date_of_birth:
            required.add(offers_pb2.OfferGroup.Required.REQUIRED_DATE_OF_BIRTH)

        if doc.required_nationality:
            required.add(offers_pb2.OfferGroup.Required.REQUIRED_NATIONALITY)

        if doc.required_passport_number:
            required.add(offers_pb2.OfferGroup.Required.REQUIRED_PASSPORT_NUMBER)

        if doc.required_expiration_date:
            required.add(offers_pb2.OfferGroup.Required.REQUIRED_EXPIRATION_DATE)

        if doc.required_issuing_country:
            required.add(offers_pb2.OfferGroup.Required.REQUIRED_ISSUING_COUNTRY)

        return required

    def _get_offer_price_requirements(
        self,
        offer_price_docs: Sequence[price.OfferPriceDoc],
    ) -> set[offers_pb2.OfferGroup.Required.ValueType]:
        required = set[offers_pb2.OfferGroup.Required.ValueType]()

        for doc in offer_price_docs or []:
            required.update(self._get_offer_price_doc_requirements(doc))

        return required

    async def _get_group_offers(  # noqa: WPS211
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
                        offer_price.itinerary.trips,
                    ),
                    price=amount.protobuf(),
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

    def _get_segment_details(  # noqa: WPS210
        self,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
        grouped_rules: Mapping[Tuple[str, str], Sequence[booking.FareRule]],
        trips: Sequence[offers.Trip],
    ) -> Sequence[offers_pb2.OfferSegmentDetails]:
        segment_details = []
        segment_baggabe_allowances = {
            segment_index: list(baggage_allowances)
            for segment_index, baggage_allowances in itertools.groupby(
                [baggage for trip in trips for baggage in trip.baggage_allowance],
                lambda baggage: baggage.segment_index,
            )
        }

        for grouped_segment in grouped_trips_segments:
            trip_segment = grouped_segment[0]
            baggage_allowance = segment_baggabe_allowances.get(
                trip_segment.segment_index,
            )
            passenger_applicable_dates = self._get_passenger_type_to_applicable_dates(
                trip_segment,
            )
            segment_details.append(
                offers_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=grouped_segment[1].id,
                    cabin_class=models_pb2.CabinClass(
                        type=models.cabin_to_proto(trip_segment.cabin),
                        marketing_name=trip_segment.cabin or "",
                    ),
                    rules=[
                        offers_pb2.SegmentRule(
                            body=rule.text,
                            title=rule.title,
                        )
                        for rule in grouped_rules[
                            (
                                trip_segment.origin.airport_code,
                                trip_segment.destination.airport_code,
                            )
                        ]
                    ],
                    baggage_allowances=[
                        offers_pb2.BaggageAllowance(
                            free=baggage.has_free_baggage,
                            applicable_to=passenger_applicable_dates[
                                baggage.passenger_type
                            ],
                        )
                        for baggage in baggage_allowance
                    ]
                    if baggage_allowance
                    else [],
                    amenities=self._transform_amenities_to_protos(
                        trip_segment.segment_amenities,
                    ),
                ),
            )

        return segment_details

    def _transform_amenities_to_protos(
        self,
        amenities: Optional[offers.SegmentAmenities],
    ) -> offers_pb2.SegmentAmenities:
        return offers_pb2.SegmentAmenities(
            beverage=self._get_amenity_option_proto(
                amenity=(amenities.beverage if amenities else None),
            ),
            entertainment=self._get_amenity_option_proto(
                amenity=(amenities.entertainment if amenities else None),
            ),
            food=self._get_amenity_option_proto(
                amenity=(amenities.food if amenities else None),
            ),
            power=self._get_amenity_option_proto(
                amenity=(amenities.power if amenities else None),
            ),
            wifi=self._get_amenity_option_proto(
                amenity=(amenities.wifi if amenities else None),
            ),
        )

    def _get_amenity_option_proto(
        self,
        amenity: Optional[offers.SegmentAmenity],
    ) -> offers_pb2.SegmentAmenity:
        if amenity is None:
            availability = offers_pb2.SegmentAmenity.Type.TYPE_UNSPECIFIED
        else:
            if amenity.exists and amenity.free:
                availability = offers_pb2.SegmentAmenity.Type.TYPE_INCLUDED
            elif amenity.exists and not amenity.free:
                availability = offers_pb2.SegmentAmenity.Type.TYPE_AVAILABLE
            else:
                availability = offers_pb2.SegmentAmenity.Type.TYPE_UNAVAILABLE

        return offers_pb2.SegmentAmenity(availability=availability)

    def _segment_to_proto(
        self,
        segment: offers.TripSegment,
        search_segment: models_pb2.Segment,
    ) -> offers_pb2.OfferSegment:
        origin = self._airports.get_by_iata(segment.origin.airport_code)
        destination = self._airports.get_by_iata(segment.destination.airport_code)

        # todo: does not handle multi-leg flights?
        return offers_pb2.OfferSegment(
            id=string.uuid(),
            segment_id=search_segment.id,
            legs=[
                offers_pb2.OfferSegmentLeg(
                    id=leg.id,
                    origin=models_pb2.Point(
                        ref=origin.identifier,
                        name=origin.airport_name or "",
                        coordinates=models_pb2.Coordinates(
                            latitude=origin.latitude,
                            longitude=origin.longitude,
                        ),
                        time_zone=origin.timezone.key,
                    ),
                    destination=models_pb2.Point(
                        ref=destination.identifier,
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
                )
                for leg in search_segment.legs
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
