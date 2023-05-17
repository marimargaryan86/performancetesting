import datetime
import itertools
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Mapping, Sequence, Tuple

from dateutil import relativedelta

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.project.junction.provider import airports, cabin_classes
from snowfall.project.junction.service.providers.ask2go import cache, models
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2, money_pb2
from snowfall.vendor.ask2go.models import booking, offers, price

_GroupedOfferSegment = Tuple[offers.TripSegment, offers_pb2.OfferSegment]
_AdultMinAge = 18
_InfantMaxAge = 2


class OfferTransformer(object):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        airport_repository: airports.AirportRepository,
        cabin_mapping_repository: cabin_classes.CabinMappingRepository,
        offer_cache: cache.OfferCache,
        price_cache: cache.PriceQuoteCache,
        offer_ttl: datetime.timedelta,
    ):
        self._airports = airport_repository
        self._cabin_mappings = cabin_mapping_repository
        self._offer_cache = offer_cache
        self._price_cache = price_cache
        self._ttl = offer_ttl

    async def to_offer_groups(
        self,
        provider_offers: AsyncIterator[offers.Offer],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        async for offer in provider_offers:
            yield await self._to_offer_group(offer)

    async def to_price_quote(
        self,
        price_result: price.OfferPriceResponse,
        option_id: str,
    ) -> offers_pb2.PriceQuote:
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        passenger_applicable_dates = self._get_passenger_type_to_applicable_dates(
            price_result.itinerary.trips[0],
        )

        return offers_pb2.PriceQuote(
            id=await self._price_cache.store(
                cache.PriceQuote(
                    pricing_id=price_result.id,
                    transaction_id=price_result.transaction_id,
                ),
                expires_at=expires_at,
            ),
            option_id=option_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            price=money.from_string(
                price_result.itinerary.pricing_information.base.total_cost,
                money.Currency(
                    price_result.itinerary.pricing_information.base.currency,
                ),
            ).protobuf(),
            required_documents=(
                self._get_offer_price_requirements(price_result.docs)
                if price_result.docs
                else None
            ),
            penalties=(
                [
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
                    for penalty in price_result.penalties
                    for information in penalty.information
                ]
                if price_result.penalties
                else []
            ),
            rules=[
                offers_pb2.FareRule(
                    body=rule.text,
                    title=rule.title,
                )
                for fare_rule in self._get_fare_rules(price_result.fare_rules)
                for rule in fare_rule.fare_rule
            ],
        )

    async def _to_offer_group(
        self,
        offer: offers.Offer,
    ) -> offers_pb2.OfferGroup:
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        grouped_offer_segments = [
            (
                segment,
                self._segment_to_proto(
                    segment=segment,
                ),
            )
            for segment_index, segment in enumerate(
                itertools.chain(
                    *[trip.segments for trip in offer.trips],
                ),
            )
        ]

        return offers_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=await self._to_options(
                offer,
                expires_at,
                grouped_offer_segments,
            ),
            segments=[grouped_segment[1] for grouped_segment in grouped_offer_segments],
        )

    def _get_offer_price_doc_requirements(
        self,
        doc: price.OfferPriceDoc,
    ) -> set[offers_pb2.PriceQuote.Required.ValueType]:
        required = set[offers_pb2.PriceQuote.Required.ValueType]()

        if doc.required_date_of_birth:
            required.add(offers_pb2.PriceQuote.REQUIRED_DATE_OF_BIRTH)

        if doc.required_nationality:
            required.add(offers_pb2.PriceQuote.REQUIRED_NATIONALITY)

        if doc.required_passport_number:
            required.add(offers_pb2.PriceQuote.REQUIRED_PASSPORT_NUMBER)

        if doc.required_expiration_date:
            required.add(offers_pb2.PriceQuote.REQUIRED_EXPIRATION_DATE)

        if doc.required_issuing_country:
            required.add(offers_pb2.PriceQuote.REQUIRED_ISSUING_COUNTRY)

        return required

    def _get_offer_price_requirements(
        self,
        offer_price_docs: Sequence[price.OfferPriceDoc],
    ) -> set[offers_pb2.PriceQuote.Required.ValueType]:
        required = set[offers_pb2.PriceQuote.Required.ValueType]()

        for doc in offer_price_docs or []:
            required.update(self._get_offer_price_doc_requirements(doc))

        return required

    async def _to_options(
        self,
        offer: offers.Offer,
        expires_at: datetime.datetime,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
    ) -> Sequence[offers_pb2.Offer]:
        group_offers = []

        branded_fares = [
            offers.BrandedPriceInformation(
                base_fare=offer.pricing_information.base.base_fare,
                total_tax=offer.pricing_information.base.total_tax,
                total_cost=offer.pricing_information.base.total_cost,
                original_cost=offer.pricing_information.base.original_cost,
                service_fee=offer.pricing_information.base.service_fee,
                currency=offer.pricing_information.base.currency,
                brand_name=(
                    offer.pricing_information.base.brand_name
                    if offer.pricing_information.base.brand_name
                    else "LOWEST FARE AVAILABLE"
                ),
                features=[
                    offers.BrandedPriceInformationfeature(
                        baggage=offer.trips[0].baggage_allowance,
                    ),
                ],
            ),
        ]
        if offer.pricing_information.additional:
            branded_fares.extend(offer.pricing_information.additional)

        for brand in branded_fares:
            amount = money.from_string(
                brand.total_cost,
                money.Currency(brand.currency),
            )

            passenger_applicable_dates = self._get_passenger_type_to_applicable_dates(
                offer.trips[0],
            )
            group_offers.append(
                offers_pb2.Offer(
                    id=await self._offer_cache.store(
                        cache.OfferDetails(
                            search_id=str(offer.search_id),
                            itinerary_id=str(offer.id),
                            brand_id=str(brand.brand_id),
                        ),
                        expires_at=expires_at,
                    ),
                    segment_details=await self._get_segment_details(
                        brand.brand_name,
                        grouped_trips_segments,
                        offer.trips,
                    ),
                    baggage_allowances=(
                        [
                            offers_pb2.BaggageAllowance(
                                free=baggage.has_free_baggage,
                                applicable_to=passenger_applicable_dates[
                                    baggage.passenger_type
                                ],
                            )
                            for baggage in brand.features[0].baggage
                        ]
                        if brand.features and brand.features[0].baggage
                        else []
                    ),
                    price=amount.protobuf(),
                    brand_name=str(brand.brand_name),
                ),
            )

        return group_offers

    async def _get_segment_details(  # noqa: WPS210
        self,
        fare_brand: str | None,
        grouped_trips_segments: Sequence[_GroupedOfferSegment],
        trips: Sequence[offers.Trip],
    ) -> Sequence[offers_pb2.OfferSegmentDetails]:
        segment_details = []
        segment_baggage_allowances = {
            segment_index: list(baggage_allowances)
            for segment_index, baggage_allowances in itertools.groupby(
                [baggage for trip in trips for baggage in trip.baggage_allowance],
                lambda baggage: baggage.segment_index,
            )
        }

        for grouped_segment in grouped_trips_segments:
            trip_segment = grouped_segment[0]
            baggage_allowance = segment_baggage_allowances.get(
                trip_segment.segment_index,
            )
            passenger_applicable_dates = self._get_passenger_type_to_applicable_dates(
                trips[0],
            )
            segment_details.append(
                offers_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=grouped_segment[1].id,
                    cabin_class=models_pb2.CabinClass(
                        type=await self._cabin_mappings.resolve_cabin_class(
                            fare_brand=fare_brand,
                            operator=str(trip_segment.operating_carrier.code),
                        ),
                        marketing_name=trip_segment.cabin or "",
                    ),
                    baggage_allowances=(
                        [
                            offers_pb2.BaggageAllowance(
                                free=baggage.has_free_baggage,
                                applicable_to=passenger_applicable_dates[
                                    baggage.passenger_type
                                ],
                            )
                            for baggage in baggage_allowance
                        ]
                        if baggage_allowance
                        else []
                    ),
                    amenities=self._transform_amenities_to_protos(
                        trip_segment.segment_amenities,
                    ),
                ),
            )

        return segment_details

    def _transform_amenities_to_protos(
        self,
        amenities: offers.SegmentAmenities | None,
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
        amenity: offers.SegmentAmenity | None,
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
    ) -> offers_pb2.OfferSegment:
        origin = self._airports.get_by_iata(segment.origin.airport_code)
        destination = self._airports.get_by_iata(segment.destination.airport_code)

        # TODO: does not handle multi-leg flights?
        return offers_pb2.OfferSegment(
            id=string.uuid(),
            legs=[
                offers_pb2.OfferSegmentLeg(
                    id=string.uuid(),
                    origin=models_pb2.Point(
                        ref=origin.identifier,
                        name=origin.airport_name or "",
                        coordinates=latlng_pb2.LatLng(
                            latitude=origin.latitude,
                            longitude=origin.longitude,
                        ),
                        time_zone=origin.timezone.key,
                    ),
                    destination=models_pb2.Point(
                        ref=destination.identifier,
                        name=destination.airport_name or "",
                        coordinates=latlng_pb2.LatLng(
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

    def _get_fare_rules(
        self,
        fare_rules: Sequence[booking.FareRules],
    ) -> Sequence[booking.FareRules]:
        for fare_rule in fare_rules:
            with suppress(IndexError):
                fare_rule.fare_rule.pop(0)

        return fare_rules

    def _get_penalty_price(
        self,
        information: price.PenaltyInformation,
    ) -> money_pb2.Money | None:
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
        first_trip: offers.Trip,
    ) -> Mapping[str, offers_pb2.ApplicableTo]:
        departure_date = first_trip.departure.date_time.date()
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
