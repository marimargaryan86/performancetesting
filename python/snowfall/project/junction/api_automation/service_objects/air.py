from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    AirOffersResult,
    AirSearchResult,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class AirClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        origin: str | None,
        destination: str | None,
        departure_after: str | None,
        passengers_dates_of_birth: Sequence[date],
    ) -> AirSearchResult:
        criteria = {}

        if origin is not None:
            criteria["origin"] = origin

        if destination is not None:
            criteria["destination"] = destination

        if departure_after is not None:
            criteria["departureAt"] = departure_after

        passengers = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")}
            for dob in passengers_dates_of_birth
        ]

        body_data = {
            "type": "air-searches",
            "attributes": {
                "criteria": criteria,
                "passengers": passengers,
            },
        }

        body = {
            "data": body_data,
        }

        url = "/air/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return AirSearchResult(result)

    async def wait_for_completed_search(self, search_id: str) -> AirSearchResult:
        search_status = await poll_until_condition_met(
            request_func=lambda: self.get_search_result(search_id),
            attribute_path="attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return AirSearchResult(search_status)

    async def get_offers(self, search_id: str) -> AirOffersResult:
        result = await self._client.request(
            method=METHOD_GET,
            url="/air/searches/{0}/results".format(search_id),
        )
        return AirOffersResult(result)

    async def get_search_result(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/air/searches/{0}".format(search_id),
        )
