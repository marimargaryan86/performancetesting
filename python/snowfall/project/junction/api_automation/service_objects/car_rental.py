from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    CarRentalOfferResult,
    CarRentalSearchResult,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class CarRentalClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        pickup_location: str | None,
        return_location: str | None,
        pickup_at: str | None,
        return_at: str | None,
        driver_age: int | None,
    ) -> CarRentalSearchResult:
        criteria: dict[str, Any] = {}

        if pickup_at is not None:
            criteria["pickupAt"] = pickup_at
        if return_at is not None:
            criteria["returnAt"] = return_at
        if driver_age is not None:
            criteria["driverAge"] = driver_age

        relationships: dict[str, Any] = {}

        if pickup_location is not None:
            relationships["origin"] = {
                "data": {
                    "id": pickup_location,
                    "type": "places",
                },
            }
        if return_location is not None:
            relationships["destination"] = {
                "data": {
                    "id": return_location,
                    "type": "places",
                },
            }

        body = {
            "data": {
                "type": "car-rental-searches",
                "attributes": criteria,
                "relationships": relationships,
            },
        }

        url = "/car-rental/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return CarRentalSearchResult(result)

    async def get_offers(self, search_id: str) -> CarRentalOfferResult:
        result = await self._client.request(
            method=METHOD_GET,
            url="/car-rental/searches/{0}/results".format(search_id),
        )
        return CarRentalOfferResult(result)

    async def wait_for_completed_search(self, search_id: str) -> CarRentalSearchResult:
        search_status = await poll_until_condition_met(
            request_func=lambda: self.get_search_result(search_id),
            attribute_path="data.attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return CarRentalSearchResult(search_status)

    async def get_search_result(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/car-rental/searches/{0}".format(search_id),
        )
