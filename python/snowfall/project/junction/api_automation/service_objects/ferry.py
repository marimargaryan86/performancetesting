from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    FerryOfferResult,
    FerrySearchResult,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class FerryClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        origin: Mapping[str, Any] | None,
        destination: Mapping[str, Any] | None,
        departure_after: str | None,
        return_at: str | None,
        passengers_dates_of_birth: Sequence[date],
    ) -> FerrySearchResult:
        criteria: dict[str, Any] = {}

        if origin is not None:
            criteria["origin"] = origin
        if destination is not None:
            criteria["destination"] = destination
        if departure_after is not None:
            criteria["departureAfter"] = departure_after
        if return_at is not None:
            criteria["returnAt"] = return_at

        criteria["passengers"] = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")}
            for dob in passengers_dates_of_birth
        ]

        body = {
            "data": {
                "type": "ferry-searches",
                "attributes": criteria,
            },
        }

        url = "/ferry/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return FerrySearchResult(result)

    async def get_offers(self, search_id: str) -> FerryOfferResult:
        result = await self._client.request(
            method=METHOD_GET,
            url="/ferry/searches/{0}/results".format(search_id),
        )
        return FerryOfferResult(result)

    async def wait_for_completed_search(self, search_id: str) -> FerrySearchResult:
        search_status = await poll_until_condition_met(
            request_func=lambda: self.get_search_result(search_id),
            attribute_path="data.attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return FerrySearchResult(search_status)

    async def get_search_result(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/ferry/searches/{0}".format(search_id),
        )
