import abc

import httpx

from snowfall.vendor.direct_ferries.clients import (
    auth,
    base,
    booking,
    operator,
    quote,
    route,
    timetable,
)
from snowfall.vendor.direct_ferries.models import booking as booking_models
from snowfall.vendor.direct_ferries.models import quote as quote_models
from snowfall.vendor.direct_ferries.models import request as request_models


class DfClient(abc.ABC):
    @property
    @abc.abstractmethod
    def routes(self) -> route.RouteClient:
        """Return client for routes."""

    @property
    @abc.abstractmethod
    def timetables(self) -> timetable.TimetableClient:
        """Return client for timetables."""

    @property
    @abc.abstractmethod
    def operators(self) -> operator.OperatorClient:
        """Return client for operators."""


class DfHttpClient(DfClient):
    """Direct Ferries API client library."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: auth.AuthClient,
        config: base.ClientConfig,
    ) -> None:
        self._routes = route.RouteHttpClient(http_client, auth_client, config)
        self._timetables = timetable.TimetableHttpClient(
            http_client,
            auth_client,
            config,
        )
        self._quotes = quote.QuoteClient(http_client, auth_client, config)
        self._operators = operator.OperatorHttpClient(
            http_client,
            auth_client,
            config,
        )
        self._bookings = booking.BookingClient(http_client, auth_client, config)

    @property
    def routes(self) -> route.RouteHttpClient:
        return self._routes

    @property
    def timetables(self) -> timetable.TimetableHttpClient:
        return self._timetables

    @property
    def quotes(self) -> quote.QuoteClient:
        return self._quotes

    @property
    def operators(self) -> operator.OperatorHttpClient:
        return self._operators

    @property
    def bookings(self) -> booking.BookingClient:
        return self._bookings

    async def create_booking(
        self,
        initial_quote: quote_models.Quote,
    ) -> booking_models.BookingResponse:
        booking_obj = await self.quotes.save(
            request=request_models.QuoteRequest(
                quote=await self.quotes.generate_quote(
                    request=request_models.QuoteRequest(
                        quote=initial_quote,
                    ),
                ),
            ),
        )
        booking_obj = await self.quotes.validate(
            booking_id=booking_obj.identifier,
            booking_token=booking_obj.booking_token,
        )

        return await self.bookings.confirm_booking(
            booking_id=booking_obj.identifier,
            booking_token=booking_obj.booking_token,
        )
