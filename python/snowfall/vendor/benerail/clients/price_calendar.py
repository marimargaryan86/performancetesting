from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.price_calendar import response as price_response

_BASE_PATH = "/price-calendar"


class PriceCalendarClient(base.BenerailBaseClient):
    async def get_price_calendars(
        self,
        origin: str,
        destination: str,
        from_date: str,
        period: str,
    ) -> price_response.PriceCalendarsResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/price-calendars".format(
                    prefix=_BASE_PATH,
                ),
                query={
                    "origin": origin,
                    "destination": destination,
                    "from-date": from_date,
                    "period": period,
                },
                headers=self._auth_headers,
            ),
        )

        return price_response.PriceCalendarsResponse(**response.json())
