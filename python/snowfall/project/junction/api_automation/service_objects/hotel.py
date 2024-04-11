import datetime
from collections.abc import Mapping, Sequence
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    HotelOfferResult,
    HotelSearchResult,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class HotelClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        latitude: float | None,
        longitude: float | None,
        checkin_at: str | None,
        checkout_at: str | None,
        radius: int | None,
        passengers: Sequence[datetime.date],
    ) -> HotelSearchResult:
        criteria: dict[str, Any] = {}

        if latitude is not None:
            criteria["latitude"] = latitude
        if longitude is not None:
            criteria["longitude"] = longitude
        if checkin_at is not None:
            criteria["checkinAt"] = checkin_at
        if checkout_at is not None:
            criteria["checkoutAt"] = checkout_at
        if radius is not None:
            criteria["radius"] = radius

        criteria["passengers"] = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")} for dob in passengers
        ]

        body = {
            "data": {
                "type": "hotel-searches",
                "attributes": criteria,
            },
        }

        url = "/hotel/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return HotelSearchResult(result)

    async def get_offers(self, search_id: str) -> HotelOfferResult:
        result = await self._client.request(
            method=METHOD_GET,
            url="/hotel/searches/{0}/results".format(search_id),
        )
        return HotelOfferResult(result)

    async def wait_for_completed_search(self, search_id: str) -> HotelSearchResult:
        search_status = await poll_until_condition_met(
            request_func=lambda: self.get_search_result(search_id),
            attribute_path="data.attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return HotelSearchResult(search_status)

    async def get_search_result(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/hotel/searches/{0}".format(search_id),
        )
