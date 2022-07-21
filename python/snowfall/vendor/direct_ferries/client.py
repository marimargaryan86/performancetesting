import httpx

from snowfall.vendor.direct_ferries.clients import auth, base
from snowfall.vendor.direct_ferries.clients import operator as operator_client
from snowfall.vendor.direct_ferries.clients import quote as quote_client
from snowfall.vendor.direct_ferries.clients import route as route_client
from snowfall.vendor.direct_ferries.clients import timetable as timetable_client


class DFClient(object):
    """Direct Ferries API client library."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: auth.AuthClient,
        config: base.ClientConfig,
    ) -> None:
        self._routes = route_client.RouteClient(http_client, auth_client, config)
        self._timetables = timetable_client.TimetableClient(
            http_client,
            auth_client,
            config,
        )
        self._quotes = quote_client.QuoteClient(http_client, auth_client, config)
        self._operators = operator_client.OperatorClient(
            http_client,
            auth_client,
            config,
        )

    @property
    def routes(self) -> route_client.RouteClient:
        return self._routes

    @property
    def timetables(self) -> timetable_client.TimetableClient:
        return self._timetables

    @property
    def quotes(self) -> quote_client.QuoteClient:
        return self._quotes

    @property
    def operators(self) -> operator_client.OperatorClient:
        return self._operators
