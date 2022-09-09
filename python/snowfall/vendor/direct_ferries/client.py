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


class DFClient(object):
    """Direct Ferries API client library."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: auth.AuthClient,
        config: base.ClientConfig,
    ) -> None:
        self._routes = route.RouteClient(http_client, auth_client, config)
        self._timetables = timetable.TimetableClient(
            http_client,
            auth_client,
            config,
        )
        self._quotes = quote.QuoteClient(http_client, auth_client, config)
        self._operators = operator.OperatorClient(
            http_client,
            auth_client,
            config,
        )
        self._bookings = booking.BookingClient(http_client, auth_client, config)

    @property
    def routes(self) -> route.RouteClient:
        return self._routes

    @property
    def timetables(self) -> timetable.TimetableClient:
        return self._timetables

    @property
    def quotes(self) -> quote.QuoteClient:
        return self._quotes

    @property
    def operators(self) -> operator.OperatorClient:
        return self._operators

    @property
    def bookings(self) -> booking.BookingClient:
        return self._bookings
