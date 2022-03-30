from typing import Any, Callable, Mapping, Optional

import httpx

from snowfall.vendor.ask2go import errors, parsers
from snowfall.vendor.ask2go.models import booking, common, price, search


class Ask2GoClient(object):  # noqa: WPS214
    def __init__(
        self,
        api_base_url: str,
        api_booking_base_url: str,
        http_client: httpx.Client,
    ) -> None:
        self._api_base_url = api_base_url
        self._api_booking_base_url = api_booking_base_url
        self._http_client = http_client

    async def create_search(
        self,
        criteria: search.CreateSearchCriteria,
    ) -> search.CreateSearchResponse:
        if criteria.inbound_date and criteria.inbound_date < criteria.outbound_date:
            raise errors.DateError(
                "Inbound date must be after outbound date, "
                + "{inbound_date} is lower than {outbound_date}".format(
                    outbound_date=criteria.outbound_date,
                    inbound_date=criteria.inbound_date,
                ),
            )

        resp = self._http_client.post(
            "{api_base_url}/search".format(api_base_url=self._api_base_url),
            json=parsers.parse_search_request(criteria),
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return search.CreateSearchResponse(**resp.json())

    async def get_search_results(
        self,
        transaction_id: str,
        search_id: str,
        page_offset: int,
    ) -> search.SearchResultsResponse:
        search_res = await self._poll(
            "{api_base_url}/search/{search_id}/{transaction_id}/{page_offset}".format(
                api_base_url=self._api_base_url,
                search_id=search_id,
                transaction_id=transaction_id,
                page_offset=page_offset,
            ),
            None,
            lambda search_data: search_data["isFinished"],
        )

        return search.SearchResultsResponse(**search_res)

    async def update_booking_billing_address(
        self,
        booking_ref_id: str,
        transaction_id: str,
    ) -> booking.Booking:
        resp = self._http_client.put(
            "{api_booking_base_url}/Booking".format(
                api_booking_base_url=self._api_booking_base_url,
            ),
            json=parsers.parse_update_booking_request(
                booking_ref_id,
                transaction_id,
            ),
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return booking.Booking(**resp.json())

    async def create_booking(
        self,
        pricing_id: str,
        transaction_id: str,
        passenger: common.Passenger,
        contact: common.Contact,
    ) -> booking.Booking:

        resp = self._http_client.post(
            "{api_booking_base_url}/Booking".format(
                api_booking_base_url=self._api_booking_base_url,
            ),
            json=parsers.parse_create_booking_request(
                pricing_id,
                transaction_id,
                passenger,
                contact,
            ),
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return booking.Booking(**resp.json())

    async def get_booking(
        self,
        booking_ref_id: str,
        transaction_id: str,
    ) -> booking.Booking:
        resp = self._http_client.get(
            "{api_booking_base_url}/Booking".format(
                api_booking_base_url=self._api_booking_base_url,
            ),
            params={
                "id": booking_ref_id,
                "transactionId": transaction_id,
            },
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return booking.Booking(**resp.json())

    async def synchronize_booking(self, booking_id: int) -> None:
        self._http_client.put(
            "{api_booking_base_url}/Sync".format(
                api_booking_base_url=self._api_booking_base_url,
            ),
            params={"bookingId": booking_id},
        )

    async def create_air_offer(
        self,
        search_id: str,
        transaction_id: str,
        offer_id: str,
    ) -> price.OfferPriceResponse:
        resp = self._http_client.put(
            "{api_base_url}/Itinerary/{search_id}/{offer_id}/Price".format(
                api_base_url=self._api_base_url,
                search_id=search_id,
                offer_id=offer_id,
            ),
            params={"transactionId": transaction_id},
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return price.OfferPriceResponse(**resp.json())

    async def _poll(
        self,
        request_url: str,
        query_params: Optional[Mapping[str, Any]],
        validator: Callable[[Mapping[str, Any]], bool],
    ) -> dict[str, Any]:
        resp = self._http_client.get(request_url, params=query_params)

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        json_data = resp.json()

        if validator(json_data):
            return json_data

        raise errors.ServiceError()
