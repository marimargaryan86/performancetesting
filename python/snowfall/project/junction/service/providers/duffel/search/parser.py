import datetime
import itertools
import zoneinfo
from typing import Sequence

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.duffel import cache, enums
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.duffel.models.offer import Offer
from snowfall.vendor.duffel.models.offer_slice import OfferSlice, OfferSliceSegment


class OfferParser(object):  # noqa: WPS214
    def __init__(
        self,
        default_ttl: datetime.timedelta,
        offer_cache: cache.OfferCache,
    ) -> None:
        self._default_ttl = default_ttl
        self._offer_cache = offer_cache

    async def parse_offer_group(
        self,
        offers: Sequence[Offer],
    ) -> offer_models_pb2.OfferGroup | None:
        if not offers:
            return None

        first_offer = offers[0]
        offer_segments = [
            self._segment_to_proto(
                segment=segment,
            )
            for segment_index, segment in enumerate(
                itertools.chain(
                    *[offer_slice.segments for offer_slice in first_offer.slices],
                ),
            )
        ]

        expires_at = self._get_expires_at(offers)
        return offer_models_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=await self._get_group_offers(offers, offer_segments, expires_at),
            segments=offer_segments,
        )

    def _get_expires_at(self, offers: Sequence[Offer]) -> datetime.datetime:
        expires_at: datetime.datetime | None = None

        for offer in offers:
            if not expires_at or expires_at < offer.expires_at:
                expires_at = offer.expires_at

        if expires_at is not None:
            return expires_at

        return datetime.datetime.now(tz=datetime.timezone.utc) + self._default_ttl

    def _segment_to_proto(
        self,
        segment: OfferSliceSegment,
    ) -> offer_models_pb2.OfferSegment:
        offer_legs = segment_to_legs(segment)

        return offer_models_pb2.OfferSegment(
            id=string.uuid(),
            legs=[
                offer_models_pb2.OfferSegmentLeg(
                    id=string.uuid(),
                    origin=models_pb2.Point(
                        ref=offer_leg.origin.iata_code or "",
                        name=offer_leg.origin.name,
                        coordinates=models_pb2.Coordinates(
                            latitude=offer_leg.origin.latitude,
                            longitude=offer_leg.origin.longitude,
                        ),
                        time_zone=offer_leg.origin.time_zone,
                    ),
                    destination=models_pb2.Point(
                        ref=offer_leg.destination.iata_code or "",
                        name=offer_leg.destination.name or "",
                        coordinates=models_pb2.Coordinates(
                            latitude=offer_leg.destination.latitude,
                            longitude=offer_leg.destination.longitude,
                        ),
                        time_zone=offer_leg.destination.time_zone,
                    ),
                    departure_at=protobuf.datetime_to_protobuf(
                        offer_leg.departing_at.replace(
                            tzinfo=zoneinfo.ZoneInfo(offer_leg.origin.time_zone),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        offer_leg.arriving_at.replace(
                            tzinfo=zoneinfo.ZoneInfo(offer_leg.destination.time_zone),
                        ),
                    ),
                )
                for offer_leg in offer_legs
            ],
            vehicle=offer_models_pb2.Vehicle(
                equipment=segment.aircraft.identifier if segment.aircraft else "",
                number=segment.marketing_carrier_flight_number,
            ),
            operator=segment.operating_carrier.iata_code or "",
            vendor=segment.marketing_carrier.iata_code or "",
            terminal=segment.origin_terminal or "",
            type=models_pb2.Schedule.TYPE_AIR,
        )

    async def _get_group_offers(
        self,
        offers: Sequence[Offer],
        offer_segments: Sequence[offer_models_pb2.OfferSegment],
        expires_at: datetime.datetime,
    ) -> Sequence[offer_models_pb2.Offer]:
        pb_offers = list[offer_models_pb2.Offer]()

        for offer in offers:
            amount = money.from_string(
                offer.total_amount,
                money.Currency(offer.total_currency),
            )
            pb_offers.append(
                offer_models_pb2.Offer(
                    id=await self._offer_cache.store(
                        cache.OfferDetails(
                            offer_id=offer.identifier,
                            total_amount=offer.total_amount,
                            currency=offer.total_currency,
                            passengers=[
                                cache.OfferDetailsPassenger(
                                    identifier=passenger.identifier,
                                    passenger_type=passenger.passenger_type,
                                )
                                for passenger in offer.passengers
                            ],
                            doc_required=offer.passenger_identity_documents_required,
                        ),
                        expires_at=expires_at,
                    ),
                    segment_details=self._parse_segment_details(
                        offer.slices,
                        offer_segments,
                    ),
                    price=amount.protobuf(),
                    brand_name=offer.slices[0].fare_brand_name or "",
                    baggage_allowances=self._parse_baggage_allowance(
                        offer.slices[0].segments[0],
                    ),
                ),
            )

        return pb_offers

    def _parse_segment_details(
        self,
        slices: Sequence[OfferSlice],
        offer_segments: Sequence[offer_models_pb2.OfferSegment],
    ) -> list[offer_models_pb2.OfferSegmentDetails]:
        duffel_segments = [
            segment for offer_slice in slices for segment in offer_slice.segments
        ]

        segment_details = []
        segment_pairs = zip(duffel_segments, offer_segments, strict=True)

        for duffel_segment, offer_segment in segment_pairs:
            segment_details.append(
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=offer_segment.id,
                    cabin_class=self._parse_cabin_class(duffel_segment),
                    baggage_allowances=self._parse_baggage_allowance(duffel_segment),
                ),
            )
        return segment_details

    def _parse_cabin_class(self, segment: OfferSliceSegment) -> models_pb2.CabinClass:
        first_passenger = segment.passengers[0] if segment.passengers else None

        if first_passenger:
            return models_pb2.CabinClass(
                type=enums.cabin_to_proto(first_passenger.cabin_class),
                marketing_name=first_passenger.cabin_class_marketing_name,
            )

        return models_pb2.CabinClass(
            type=enums.cabin_to_proto(None),
        )

    def _parse_baggage_allowance(
        self,
        offer_segment: OfferSliceSegment,
    ) -> list[offer_models_pb2.BaggageAllowance]:
        return [
            offer_models_pb2.BaggageAllowance(
                free=self._free_checked_baggage(offer_segment) > 0,
            ),
        ]

    def _free_checked_baggage(self, offer_segment: OfferSliceSegment) -> int:
        return sum(
            baggage.quantity
            for passenger in offer_segment.passengers
            for baggage in passenger.baggages
            if baggage.baggage_type == "checked"
        )


def segment_to_legs(
    segment: OfferSliceSegment,
) -> Sequence[OfferSliceSegment]:
    if not segment.stops:
        return [segment]

    legs = [segment.copy()]

    for stop in segment.stops:
        last_leg = legs[-1]

        legs.append(
            OfferSliceSegment(
                identifier=last_leg.identifier,
                aircraft=last_leg.aircraft,
                arriving_at=last_leg.arriving_at,
                departing_at=stop.departing_at,
                destination=last_leg.destination,
                destination_terminal=last_leg.destination_terminal,
                origin=stop.airport,
                marketing_carrier=last_leg.marketing_carrier,
                marketing_carrier_flight_number=last_leg.marketing_carrier_flight_number,
                operating_carrier=last_leg.operating_carrier,
                operating_carrier_flight_number=last_leg.operating_carrier_flight_number,
                passengers=last_leg.passengers,
            ),
        )

        last_leg.destination = stop.airport
        last_leg.destination_terminal = None
        last_leg.arriving_at = stop.arriving_at

    return legs
