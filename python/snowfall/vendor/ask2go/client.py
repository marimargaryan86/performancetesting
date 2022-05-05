import contextlib
import http
import inspect
import json
from typing import Awaitable

import httpx

from snowfall.vendor.ask2go import errors, parsers
from snowfall.vendor.ask2go.models import booking, common, price, search


async def _make_request(promise: Awaitable[httpx.Response]) -> httpx.Response:
    try:
        response = await promise
    except httpx.HTTPError as raw_exc:
        raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

    try:
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise errors.ServiceError(_get_response_error_message(response)) from exc

    return response


def _get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)


class Ask2GoClient(object):  # noqa: WPS214
    def __init__(
        self,
        api_base_url: str,
        api_booking_base_url: str,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._api_base_url = api_base_url
        self._api_booking_base_url = api_booking_base_url
        self._http_client = http_client

    async def get_airports(self) -> list[common.Airport]:
        response = await _make_request(
            self._http_client.get(
                "{api_base_url}/Airports".format(api_base_url=self._api_base_url),
            ),
        )

        return [common.Airport(**airport) for airport in response.json()["airport"]]

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

        response = await _make_request(
            self._http_client.post(
                "{api_base_url}/search".format(api_base_url=self._api_base_url),
                json=parsers.parse_search_request(criteria),
            ),
        )

        return search.CreateSearchResponse(**response.json())

    async def get_search_results(
        self,
        transaction_id: str,
        search_id: str,
        page_offset: int,
    ) -> search.SearchResultsResponse:
        response = await _make_request(
            self._http_client.get(
                "{api_base_url}/search/{search_id}/{transaction_id}/{page_offset}".format(
                    api_base_url=self._api_base_url,
                    search_id=search_id,
                    transaction_id=transaction_id,
                    page_offset=page_offset,
                ),
            ),
        )

        return search.SearchResultsResponse(**response.json())

    async def update_booking_billing_address(
        self,
        booking_ref_id: str,
        transaction_id: str,
    ) -> booking.Booking:
        response = await _make_request(
            self._http_client.put(
                "{api_booking_base_url}/Booking".format(
                    api_booking_base_url=self._api_booking_base_url,
                ),
                json=parsers.parse_update_booking_request(
                    booking_ref_id,
                    transaction_id,
                ),
            ),
        )

        return booking.Booking(**response.json())

    async def create_booking(
        self,
        pricing_id: str,
        transaction_id: str,
        passenger: common.Passenger,
        contact: common.Contact,
    ) -> booking.Booking:

        response = await _make_request(
            self._http_client.post(
                "{api_booking_base_url}/Booking".format(
                    api_booking_base_url=self._api_booking_base_url,
                ),
                json=parsers.parse_create_booking_request(
                    pricing_id,
                    transaction_id,
                    passenger,
                    contact,
                ),
            ),
        )

        return booking.Booking(**response.json())

    async def get_booking(
        self,
        booking_ref_id: str,
        transaction_id: str,
    ) -> booking.Booking:
        response = await _make_request(
            self._http_client.get(
                "{api_booking_base_url}/Booking".format(
                    api_booking_base_url=self._api_booking_base_url,
                ),
                params={
                    "id": booking_ref_id,
                    "transactionId": transaction_id,
                },
            ),
        )

        return booking.Booking(**response.json())

    async def synchronize_booking(self, booking_id: int) -> None:
        await self._http_client.put(
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
        response = await _make_request(
            self._http_client.put(
                "{api_base_url}/Itinerary/{search_id}/{offer_id}/Price".format(
                    api_base_url=self._api_base_url,
                    search_id=search_id,
                    offer_id=offer_id,
                ),
                params={"transactionId": transaction_id},
            ),
        )

        return price.OfferPriceResponse(**response.json())
