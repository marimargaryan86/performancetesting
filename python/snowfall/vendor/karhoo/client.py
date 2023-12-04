import datetime

import httpx

from snowfall.stdlib.transport.http import client
from snowfall.vendor.karhoo import parsers
from snowfall.vendor.karhoo.models import bookings, fares, location, quotes


class KarhooClient(client.HttpClient):
    def __init__(self, api_key: str, base_url: str, http_client: httpx.AsyncClient):
        super().__init__(base_url, http_client)
        self._api_key = api_key

    async def request_quotes(
        self,
        origin: location.Coordinates,
        destination: location.Coordinates,
        departure_at: datetime.datetime | None = None,
    ) -> quotes.RequestQuotesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="/v2/quotes",
                payload=parsers.parse_request_quotes_request(
                    origin,
                    destination,
                    departure_at,
                ),
                headers=self._auth_header,
            ),
        )
        return quotes.RequestQuotesResponse(**response.json())

    async def list_quotes(
        self,
        ident: str,
        min_passengers: int | None = None,
    ) -> quotes.RequestQuotesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="/v2/quotes/{ident}".format(ident=ident),
                headers=self._auth_header,
                query={"passengers": str(min_passengers)} if min_passengers else {},
            ),
        )

        return quotes.RequestQuotesResponse(**response.json())

    async def book_trip(
        self,
        booking: bookings.Booking,
    ) -> bookings.BookingResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="/v1/bookings",
                payload=parsers.parse_book_trip(booking),
                headers=self._auth_header,
            ),
        )

        return bookings.BookingResponse(**response.json())

    async def get_booking_details(
        self,
        ident: str,
    ) -> bookings.BookingResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="/v1/bookings/{ident}".format(ident=ident),
                headers=self._auth_header,
            ),
        )

        return bookings.BookingResponse(**response.json())

    async def cancel_booking(
        self,
        ident: str,
        reason: bookings.CANCELLATION_REASON,
        explanation: str | None,
    ) -> None:
        await self._make_request(
            client.RequestOptions(
                method="POST",
                path="/v1/bookings/{ident}".format(ident=ident),
                payload={
                    "reason": reason,
                    "explanation": explanation,
                },
                headers=self._auth_header,
            ),
        )

    async def get_position_of_trip(
        self,
        ident: str,
    ) -> location.TripPositionResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="/v1/bookings/{ident}/track".format(ident=ident),
                headers=self._auth_header,
            ),
        )

        return location.TripPositionResponse(**response.json())

    async def get_final_fare(self, trip_id: str) -> fares.FinalFare:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="/v1/fares/trip/{trip_id}".format(trip_id=trip_id),
                headers=self._auth_header,
            ),
        )

        return fares.FinalFare(**response.json())

    @property
    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": "ApiKey {api_key}".format(api_key=self._api_key)}
