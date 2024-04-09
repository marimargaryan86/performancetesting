import json
from collections.abc import Sequence

import httpx

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import common, quote, ticket
from snowfall.vendor.direct_ferries.models import request as request_models

_GET_METHOD = "get"
_POST_METHOD = "post"
_DATA_KEY = "data"
_ROUTES_KEY = "routes"


class QuoteClient(base.BaseClient):
    async def get_quotes(
        self,
        request: request_models.QuoteRequest,
    ) -> Sequence[quote.Quote]:
        request.quote.partner_code = self._config.partner_code

        url = "{0}/api/{1}/Quotes/get-quotes-request".format(
            self._config.api_url,
            self._config.api_version,
        )

        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_POST_METHOD,
                    url=url,
                    payload=request.json(by_alias=True),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return [
            quote.Quote(**quote_data)
            for quote_data in response_data[_DATA_KEY]["quotes"]
        ]

    async def get_accommodations(
        self,
        request: request_models.QuoteRequest,
    ) -> quote.AccommodationResponse:
        request.quote.partner_code = self._config.partner_code

        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/get-accommodation-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    payload=request.json(by_alias=True),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return quote.AccommodationResponse(**response_data[_DATA_KEY])

    async def get_ticket_types(
        self,
        request: request_models.QuoteRequest,
    ) -> ticket.TicketTypesResponse:
        request.quote.partner_code = self._config.partner_code

        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/get-ticket-types-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    payload=request.json(by_alias=True),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return ticket.TicketTypesResponse(**response_data[_DATA_KEY])

    async def generate_quote(
        self,
        request: request_models.QuoteRequest,
    ) -> quote.Quote:
        request.quote.partner_code = self._config.partner_code

        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/generate-quote-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    payload=request.json(by_alias=True),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return quote.Quote(**response_data[_DATA_KEY]["quote"])

    async def save(
        self,
        request: request_models.QuoteRequest,
    ) -> common.Booking:
        request.quote.partner_code = self._config.partner_code

        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Quotes/save-quote-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    method=_POST_METHOD,
                    payload=request.json(by_alias=True),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return common.Booking(**response_data[_DATA_KEY]["booking"])

    async def validate(
        self,
        booking_id: int,
        booking_token: str,
    ) -> common.Booking:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Quotes/validate-quote-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    method=_POST_METHOD,
                    payload=json.dumps(
                        {
                            "bookingId": booking_id,
                            "bookingToken": booking_token,
                        },
                    ),
                    query_params=httpx.QueryParams(self._request_params),
                ),
            )
        ).json()

        return common.Booking(**response_data[_DATA_KEY]["booking"])
