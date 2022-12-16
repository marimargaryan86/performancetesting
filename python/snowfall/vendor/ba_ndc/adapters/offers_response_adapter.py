import datetime
from typing import Mapping

from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_passenger_schemas,
    response_offer_search_schemas,
)


class OffersResponseAdapter(object):
    offers_response: response_offer_search_schemas.OfferSearchResponse
    segments: Mapping[str, response_common_offer_schemas.Segment]
    price_classes: Mapping[str, response_common_offer_schemas.PriceClass]

    def __init__(
        self,
        offers_response: response_offer_search_schemas.OfferSearchResponse,
    ) -> None:
        self.offers_response = offers_response
        self.segments = {
            segment.identifier: segment for segment in offers_response.segments
        }
        self.price_classes = {
            price_c.identifier: price_c for price_c in offers_response.price_classes
        }

    def get_offers(self) -> list[response_offer_search_schemas.Offer]:
        return self.offers_response.offers

    def get_passengers(self) -> list[response_common_passenger_schemas.PassengerSimple]:
        return self.offers_response.passengers

    def get_expires_at(self) -> datetime.datetime:
        return self.offers_response.expires_at

    def get_segment_by_id(
        self,
        segment_id: str,
    ) -> response_common_offer_schemas.Segment | None:
        return self.segments.get(segment_id)

    def get_price_class_by_id(
        self,
        price_class_id: str,
    ) -> response_common_offer_schemas.PriceClass | None:
        return self.price_classes.get(price_class_id)

    def get_brand_name(
        self,
        offer: response_offer_search_schemas.Offer,
    ) -> str:
        if offer and offer.trips:
            price_class = self.get_price_class_by_id(offer.trips[0].price_class_id)

            if price_class:
                return price_class.name

        return ""
