import hashlib
import json
from collections.abc import Mapping, Sequence

from snowfall.project.junction.service.providers.duffel import cache
from snowfall.project.junction.service.providers.duffel.client_factory import (
    DuffelClientFactory,
)
from snowfall.stdlib.logging import stdout
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders.offer_request import OffersRequestBuilder
from snowfall.vendor.duffel.errors import DuffelError
from snowfall.vendor.duffel.models.offer import Offer, PrivateFare
from snowfall.vendor.duffel.models.offer_request import OfferRequest


class PricingAdapter(object):
    def __init__(
        self,
        duffel_client: client.DuffelClient,
    ) -> None:
        self._client = duffel_client
        self._logger = stdout.get_logger()

    async def get_price_quote(self, offer_details: cache.OfferDetails) -> Offer:
        return await self._client.get_single_offer(offer_details.offer_id)

    async def refresh_offer(
        self,
        offer_details: cache.OfferDetails,
        private_fares: Mapping[str, Sequence[PrivateFare]] | None = None,
    ) -> Offer:
        offer = await self._client.get_single_offer(offer_details.offer_id)

        offers_request_builder = OffersRequestBuilder().with_offer(offer, private_fares)

        offers = await self._client.create_offer_request(
            offers_request_builder.build(),
        )

        renewed_offer = self._find_same_offer(offers, offer)

        if renewed_offer is None:
            self._logger.error(
                "Pricing failed",
                reson="Offer is not available anymore",
                offer_id=offer_details.offer_id,
            )
            raise DuffelError("Offer is not available anymore")

        return renewed_offer

    def _find_same_offer(self, offers: OfferRequest, offer: Offer) -> Offer | None:
        offer_hash = self._get_offer_hash(offer)

        for offers_offer in offers.offers:
            if self._get_offer_hash(offers_offer) == offer_hash:
                return offers_offer

        return None

    def _get_offer_hash(self, offer: Offer) -> str:
        reduced_offer = {
            "slices": [
                {
                    "segments": [
                        {
                            "passengers": [
                                {
                                    "fare_basis_code": passenger.fare_basis_code,
                                    "cabin_class_marketing_name": (
                                        passenger.cabin_class_marketing_name
                                    ),
                                    "cabin_class": passenger.cabin_class,
                                }
                                for passenger in segment.passengers
                            ],
                            "origin": segment.origin.iata_code,
                            "destination": segment.destination.iata_code,
                            "operating_flight_number": (
                                segment.operating_carrier_flight_number
                            ),
                            "operating_carrier_code": (
                                segment.operating_carrier.iata_code
                            ),
                            "marketing_carrier_code": (
                                segment.marketing_carrier.iata_code
                            ),
                            "marketing_flight_number": (
                                segment.marketing_carrier_flight_number
                            ),
                            "departing_at": segment.departing_at,
                            "arriving_at": segment.arriving_at,
                        }
                        for segment in offer_slice.segments
                    ],
                    "fare_brand_name": offer_slice.fare_brand_name,
                }
                for offer_slice in offer.slices
            ],
        }

        return hashlib.md5(
            json.dumps(reduced_offer, sort_keys=True, default=str).encode(),
            usedforsecurity=False,
        ).hexdigest()


class PricingAdapterFactory(object):
    def __init__(self, duffel_client_factory: DuffelClientFactory):
        self._duffel_client_factory = duffel_client_factory

    def for_reseller(self, reseller_id: str) -> PricingAdapter:
        return PricingAdapter(
            duffel_client=self._duffel_client_factory.for_reseller(reseller_id),
        )
