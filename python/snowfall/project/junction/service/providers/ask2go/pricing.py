import asyncio

import tenacity

from snowfall.project.junction.service.providers.ask2go import cache
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout
from snowfall.vendor.ask2go import client, errors
from snowfall.vendor.ask2go.models import price

_SUCCESSFUL_PRICE_STATUSES = ("PricingSuccedded", "PriceDifference")
_FAILED_PRICE_STATUSES = ("PricingFailed", "Unknown")


class NoPricingError(Exception):
    """Raised when a failed pricing result is received."""


class PricingTimeoutError(Exception):
    """Raised when no successful pricing result is received within the time limit."""


class Adapter(object):
    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        poll_retries_limit: int = 10,
        wait_time_between_polling: float = 2,
    ):
        self._client = ask2go_client
        self._poll_retries_limit = poll_retries_limit
        self._wait_time_between_polling = wait_time_between_polling
        self._logger = stdout.get_logger()

    async def get_price_quote(
        self,
        session_token: str,
        offer_details: cache.OfferDetails,
    ) -> price.OfferPriceResponse:
        with stdout.context_binding(
            search_id=offer_details.search_id,
            offer_id=offer_details.itinerary_id,
            brand_id=offer_details.brand_id,
        ):
            async_offer = await self._client.create_air_offer_async(
                search_id=offer_details.search_id,
                offer_id=offer_details.itinerary_id,
                brand_id=offer_details.brand_id,
                transaction_id=string.to_uuid(session_token),
            )

            try:
                return await self._get_async_price_result(async_offer)
            except (NoPricingError, PricingTimeoutError) as err:
                self._logger.error("Pricing failed", exception=str(type(err).__name__))
                raise

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(10),
        retry=tenacity.retry_if_exception_type(errors.TimeOutError),
        wait=tenacity.wait_random_exponential(multiplier=1, max=5),
        reraise=True,
    )
    async def _get_async_price_result(
        self,
        async_offer: price.AsyncOfferPriceResponse,
    ) -> price.OfferPriceResponse:
        for _ in range(self._poll_retries_limit):
            await asyncio.sleep(self._wait_time_between_polling)

            price_result = await self._client.get_air_offer_result(
                transaction_id=async_offer.transaction_id,
                pricing_id=async_offer.id,
            )

            if not price_result:
                continue

            if price_result.information.status in _SUCCESSFUL_PRICE_STATUSES:
                return price_result

            if self._failed_pricing(price_result):
                raise NoPricingError("Pricing did not succeed.")

        raise PricingTimeoutError("Pricing timed out after maximum retries.")

    def _failed_pricing(self, price_result: price.OfferPriceResponse) -> bool:
        return (
            price_result.information.status in _FAILED_PRICE_STATUSES
            or not price_result.itinerary.pricing_information.base.total_cost
        )
