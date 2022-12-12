import structlog

from snowfall.project.junction.service.providers.duffel import cache
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.errors import ServiceError
from snowfall.vendor.duffel.models.offer import Offer


class PricingAdapter(object):
    def __init__(
        self,
        duffel_client: client.DuffelClient,
    ) -> None:
        self._client = duffel_client
        self._logger = structlog.get_logger(__name__)

    async def get_price_quote(self, offer_details: cache.OfferDetails) -> Offer:
        try:
            offer = await self._client.get_single_offer(offer_details.offer_id)
        except ServiceError as ex:
            self._logger.error("Pricing failed", exception=str(type(ex).__name__))
            raise

        return offer
