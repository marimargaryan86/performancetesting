import asyncio
import inspect
from collections.abc import Sequence
from typing import Any

import httpx

from snowfall.stdlib import string
from snowfall.vendor.ask2go import errors, parsers
from snowfall.vendor.ask2go.models import (
    booking,
    common,
    price,
    search,
    seat_map,
    validate_offer_criteria,
    validated_offer,
)
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


class Ask2GoClient(object):  # noqa: WPS214
    def __init__(
        self,
        api_base_url: str,
        api_booking_base_url: str,
        http_client: httpx.AsyncClient,
        rate_limit_client: RateLimitClient | None = None,
    ) -> None:
        self._api_base_url = httpx.URL(api_base_url)
        self._api_booking_base_url = httpx.URL(api_booking_base_url)
        self._http_client = http_client
        self._rate_limit_client = rate_limit_client

    async def get_airports(self) -> list[common.Airport]:
        response = await self._make_request(
            "GET",
            self._api_base_url.copy_with(
                path="/api/Airports",
            ),
        )

        return [common.Airport(**airport) for airport in response.json()["airport"]]

    async def create_search(
        self,
        criteria: search.CreateSearchCriteria,
        rate_limit_timeout: float = 60,
    ) -> search.CreateSearchResponse:
        if criteria.inbound_date and criteria.inbound_date < criteria.outbound_date:
            raise errors.DateError(
                "Inbound date must be after outbound date, "
                + "{inbound_date} is lower than {outbound_date}".format(
                    outbound_date=criteria.outbound_date,
                    inbound_date=criteria.inbound_date,
                ),
            )

        response = await self._make_request(
            "POST",
            self._api_base_url.copy_with(
                path="/api/search",
            ),
            payload=parsers.parse_search_request(criteria),
            rate_limit_timeout=rate_limit_timeout,
        )

        return search.CreateSearchResponse(**response.json())

    async def get_search_results(
        self,
        transaction_id: str,
        search_id: str,
        page_offset: int,
        rate_limit_timeout: float = 60,
    ) -> search.SearchResultsResponse:
        response = await self._make_request(
            "GET",
            self._api_base_url.copy_with(
                path="/api/search/{search_id}/{transaction_id}/{page_offset}".format(
                    search_id=search_id,
                    transaction_id=transaction_id,
                    page_offset=page_offset,
                ),
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return search.SearchResultsResponse(**response.json())

    # Orders
    async def update_booking_billing_address(
        self,
        booking_ref_id: str,
        transaction_id: str,
        *,
        override_double_booking_check: bool,
    ) -> booking.Booking:
        response = await self._make_request(
            "PUT",
            self._api_booking_base_url.copy_with(
                path="/api/Booking",
            ),
            payload=parsers.parse_update_booking_request(
                booking_ref_id=booking_ref_id,
                transaction_id=transaction_id,
                override_double_booking_check=override_double_booking_check,
            ),
        )

        return booking.Booking(**response.json())

    # Orders
    async def create_booking(
        self,
        pricing_id: str,
        transaction_id: str,
        passengers: Sequence[common.Passenger],
        contact: common.Contact,
    ) -> booking.Booking:
        response = await self._make_request(
            "POST",
            self._api_booking_base_url.copy_with(
                path="/api/Booking",
            ),
            payload=parsers.parse_create_booking_request(
                pricing_id,
                transaction_id,
                passengers,
                contact,
            ),
        )

        return booking.Booking(**response.json())

    # Orders
    async def get_booking(
        self,
        booking_ref_id: str,
        transaction_id: str,
    ) -> tuple[booking.Booking, bytes]:
        response = await self._make_request(
            "GET",
            self._api_booking_base_url.copy_with(
                path="/api/Booking",
                params={
                    "id": booking_ref_id,
                    "transactionId": transaction_id,
                },
            ),
        )

        return booking.Booking(**response.json()), response.content

    async def synchronize_booking(self, booking_id: int) -> None:
        await self._make_request(
            "PUT",
            self._api_booking_base_url.copy_with(
                path="/api/Sync",
                params={"bookingId": booking_id},
            ),
        )

    async def cancel_booking(self, booking_id: str | int, record_locator: str) -> None:
        await self._make_request(
            "DELETE",
            self._api_booking_base_url.copy_with(
                path="/api/Booking",
            ),
            payload={"bookingId": int(booking_id), "recordLocator": record_locator},
        )

    async def create_air_offer(
        self,
        search_id: str,
        transaction_id: str,
        offer_id: str,
        brand_id: str | None = None,
    ) -> price.OfferPriceResponse:
        response = await self._make_request(
            "PUT",
            self._api_base_url.copy_with(
                path="/api/Itinerary/{search_id}/{offer_id}/Price".format(
                    search_id=search_id,
                    offer_id=offer_id,
                ),
                params={
                    "transactionId": transaction_id,
                    **({"brandId": brand_id} if brand_id else {}),
                },
            ),
        )

        return price.OfferPriceResponse(**response.json())

    # pricing
    async def create_air_offer_async(
        self,
        search_id: str,
        offer_id: str,
        transaction_id: str | None = None,
        brand_id: str | None = None,
        rate_limit_timeout: float = 60,
    ) -> price.AsyncOfferPriceResponse:
        response = await self._make_request(
            "PUT",
            self._api_base_url.copy_with(path="/api/Itinerary/PriceAsync"),
            payload={
                "searchId": search_id,
                "itineraryId": offer_id,
                **({"brandId": brand_id} if brand_id else {}),
                **({"transactionId": transaction_id} if transaction_id else {}),
            },
            rate_limit_timeout=rate_limit_timeout,
        )

        return price.AsyncOfferPriceResponse(**response.json())

    # pricing
    async def get_air_offer_result(
        self,
        transaction_id: str,
        pricing_id: str,
        rate_limit_timeout: float = 60,
    ) -> price.OfferPriceResponse | None:
        response = await self._make_request(
            "GET",
            self._api_base_url.copy_with(
                path="/api/Itinerary/{pricing_id}/{transaction_id}/GetPrice".format(
                    transaction_id=transaction_id,
                    pricing_id=pricing_id,
                ),
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        json_data = response.json()

        if not json_data["hasFinished"]:
            return None

        return price.OfferPriceResponse(**json_data)

    async def validate_offer(
        self,
        criteria: validate_offer_criteria.ValidateOfferCriteria,
    ) -> validate_offer_criteria.ValidateOfferResponse:
        response = await self._make_request(
            "POST",
            self._api_base_url.copy_with(
                path="/api/Itinerary/Validate",
            ),
            payload=parsers.parse_validated_offer_criteria(criteria),
        )

        return validate_offer_criteria.ValidateOfferResponse(**response.json())

    async def get_validated_offer(
        self,
        pricing_id: str,
        transaction_id: str,
    ) -> validated_offer.ValidatedOfferResponse | None:
        response = await self._make_request(
            "GET",
            self._api_base_url.copy_with(
                path="/api/Itinerary/Validate/{pricing_id}/{transaction_id}".format(
                    pricing_id=pricing_id,
                    transaction_id=transaction_id,
                ),
            ),
        )

        if not response.content:
            return None

        return validated_offer.ValidatedOfferResponse(**response.json())

    async def get_seat_map(
        self,
        search_id: str,
        itinerary_id: str,
        brand_id: str | None = None,
    ) -> seat_map.SeatMapResponse:
        transaction_id = string.uuid()

        response = await self._make_request(
            "GET",
            self._api_base_url.copy_with(
                path="/api/seatmap/{search_id}/{itinerary_id}".format(
                    search_id=search_id,
                    itinerary_id=itinerary_id,
                ),
                params={
                    "transactionId": transaction_id,
                    **({"brandId": brand_id} if brand_id else {}),
                },
            ),
        )
        return seat_map.SeatMapResponse(**response.json())

    async def _make_request(  # noqa: WPS238
        self,
        method: str,
        url: httpx.URL,
        payload: Any | None = None,
        rate_limit_timeout: float = 60,
    ) -> httpx.Response:
        if self._rate_limit_client:
            try:
                await self._rate_limit_client.rate_limit(timeout=rate_limit_timeout)
            except asyncio.TimeoutError as raw_exc:
                raise errors.AsyncTimeOutError(inspect.getdoc(raw_exc)) from raw_exc
        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=payload,
            )
        except httpx.TimeoutException as timeout_exc:
            raise errors.TimeOutError.from_error(timeout_exc) from timeout_exc
        except httpx.RequestError as request_exc:
            raise errors.RequestError.from_error(request_exc) from request_exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise errors.HttpStatusError.from_error(exc) from exc

        return response
