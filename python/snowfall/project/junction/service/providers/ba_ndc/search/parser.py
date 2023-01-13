import itertools
from typing import List, Sequence

from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.ba_ndc import cache, enums
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_order_schemas,
    response_offer_search_schemas,
    response_priced_offer_schemas,
)
from snowfall.vendor.ba_ndc.models.util import offer_enums


def _parse_cabin_class(
    price_class: response_common_offer_schemas.PriceClass | None,
) -> models_pb2.CabinClass:
    if price_class:
        return models_pb2.CabinClass(
            type=enums.cabin_to_proto(price_class.cabin_type),
            marketing_name=price_class.name,
        )

    return models_pb2.CabinClass(
        type=enums.cabin_to_proto(None),
    )


def _parse_baggage_allowance(
    bag_allowances: Sequence[response_priced_offer_schemas.BagAllowance],
) -> List[offer_models_pb2.BaggageAllowance]:
    return [
        offer_models_pb2.BaggageAllowance(
            free=free_checked_baggage(bag_allowances) > 0,
        ),
    ]


def free_checked_baggage(
    bag_allowances: Sequence[response_priced_offer_schemas.BagAllowance],
) -> int:
    return sum(
        piece_allowance.quantity
        for bag_allowance in bag_allowances
        for piece_allowance in bag_allowance.piece_allowance
        if bag_allowance.category == offer_enums.BagCategoryEnum.checked
    )


def _parse_segment_details(  # noqa: WPS210
    trips: Sequence[response_common_offer_schemas.Trip],
    offer_segments: Sequence[offer_models_pb2.OfferSegment],
    offers_adapter: OffersResponseAdapter,
) -> List[offer_models_pb2.OfferSegmentDetails]:
    segment_details = []

    for trip in trips:
        for _ba_ndc_segment, offer_segment in zip(trip.segment_ids, offer_segments):
            bag_allowances: list[response_priced_offer_schemas.BagAllowance] = []

            for bag_ref in trip.baggage_allowance_refs:
                bag_allowance = offers_adapter.get_bag_allowance_by_id(bag_ref)

                if bag_allowance:
                    bag_allowances.append(bag_allowance)

            segment_details.append(
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=offer_segment.id,
                    cabin_class=_parse_cabin_class(
                        offers_adapter.get_price_class_by_id(trip.price_class_id),
                    ),
                    baggage_allowances=_parse_baggage_allowance(bag_allowances),
                ),
            )
    return segment_details


def _segment_to_proto(
    segment: response_common_offer_schemas.Segment | None,
    search_segment: models_pb2.Segment,
) -> offer_models_pb2.OfferSegment | None:
    first_search_segment_leg = search_segment.legs[0]
    # todo: add support of stops

    if segment:
        leg = offer_models_pb2.OfferSegmentLeg(
            id=first_search_segment_leg.id,
            origin=models_pb2.Point(
                ref=segment.origin.code or "",
                name=segment.origin.name or "",
                coordinates=models_pb2.Coordinates(
                    latitude=first_search_segment_leg.origin.coordinates.latitude,
                    longitude=first_search_segment_leg.origin.coordinates.longitude,
                ),
                time_zone=first_search_segment_leg.origin.time_zone,
            ),
            destination=models_pb2.Point(
                ref=segment.destination.code or "",
                name=segment.destination.name or "",
                coordinates=models_pb2.Coordinates(
                    latitude=first_search_segment_leg.destination.coordinates.latitude,
                    longitude=first_search_segment_leg.destination.coordinates.longitude,
                ),
                time_zone=first_search_segment_leg.origin.time_zone,
            ),
            departure_at=protobuf.datetime_to_protobuf(segment.departure_date_time),
            arrival_at=protobuf.datetime_to_protobuf(segment.arrival_date_time),
        )

        return offer_models_pb2.OfferSegment(
            id=string.uuid(),
            segment_id=search_segment.id,
            legs=[leg],
            vehicle=offer_models_pb2.Vehicle(
                equipment=segment.equipment.code if segment.equipment else "",
                number=segment.marketing_carrier.flight_number or "",
            ),
            operator=segment.operating_carrier.airline_id
            if segment.operating_carrier
            else "",
            vendor=segment.marketing_carrier.airline_id or "",
            terminal=segment.destination.terminal_name or "",
            type=models_pb2.Schedule.TYPE_AIR,
        )

    return None


def get_penalties(
    trips: Sequence[response_common_offer_schemas.Trip],
    offers_adapter: OffersResponseAdapter,
) -> List[cache.OfferPenalty]:
    penalties = []
    penalty_ids = [
        penalty_id for trip in trips for penalty_id in trip.penalty_ids or []
    ]

    for penalty_id in penalty_ids:
        penalty = offers_adapter.get_penalty_by_id(penalty_id)

        if penalty:
            penalties.append(to_offer_penalty(penalty))

    return penalties


def to_offer_penalty(
    penalty: response_common_order_schemas.Penalty,
) -> cache.OfferPenalty:
    return cache.OfferPenalty(
        penalty_type=penalty.penalty_type.value,
        price=cache.Price(
            amount=penalty.price.total_amount if penalty.price else "",
            currency=penalty.price.currency if penalty.price else "",
        ),
    )


def _get_doc_required(offer_segments: Sequence[offer_models_pb2.OfferSegment]) -> bool:
    return False  # TODO return this properly


class OfferParser(object):
    def __init__(
        self,
        offer_cache: cache.OfferCache,
    ) -> None:
        self._offer_cache = offer_cache

    async def parse_offer_group(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offers: Sequence[response_offer_search_schemas.Offer],
        offers_adapter: OffersResponseAdapter,
    ) -> offer_models_pb2.OfferGroup | None:
        if not offers:
            return None

        first_offer = offers[0]
        offer_segments = [
            _segment_to_proto(
                segment=offers_adapter.get_segment_by_id(segment),
                search_segment=search_task.segments[segment_index],
            )
            for segment_index, segment in enumerate(
                itertools.chain(
                    *[trip.segment_ids for trip in first_offer.trips],
                ),
            )
        ]

        offer_segm = [of_seg for of_seg in offer_segments if of_seg is not None]

        if not offer_segm:
            return None

        return offer_models_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(offers_adapter.get_expires_at()),
            offers=await self._get_group_offers(
                offers,
                offer_segm,
                offers_adapter,
            ),
            segments=offer_segm,
        )

    async def _get_group_offers(
        self,
        offers: Sequence[response_offer_search_schemas.Offer],
        offer_segments: Sequence[offer_models_pb2.OfferSegment],
        offers_adapter: OffersResponseAdapter,
    ) -> Sequence[offer_models_pb2.Offer]:
        pb_offers = list[offer_models_pb2.Offer]()

        for offer in offers:
            amount = money.from_string(
                offer.price.total_amount,
                money.Currency(offer.price.currency),
            )
            pb_offers.append(
                offer_models_pb2.Offer(
                    id=await self._offer_cache.store(
                        cache.OfferDetails(
                            offer_id=offer.identifier,
                            price=cache.Price(
                                amount=offer.price.total_amount,
                                currency=offer.price.currency,
                            ),
                            passengers=[
                                cache.OfferDetailsPassenger(
                                    identifier=passenger_info.identifier,
                                    passenger_type=passenger_info.passenger_type.name,
                                )
                                for passenger_info in offers_adapter.get_passengers()
                            ],
                            expires_at=offers_adapter.get_expires_at(),
                            penalties=get_penalties(offer.trips, offers_adapter),
                            doc_required=_get_doc_required(offer_segments),
                        ),
                        expires_at=offers_adapter.get_expires_at(),
                    ),
                    segment_details=_parse_segment_details(
                        offer.trips,
                        offer_segments,
                        offers_adapter,
                    ),
                    price=amount.protobuf(),
                    brand_name=offers_adapter.get_brand_name(offer),
                ),
            )

        return pb_offers
