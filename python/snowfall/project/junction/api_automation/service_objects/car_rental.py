from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    CarRentalResultData,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class CarRentalClient(object):
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        pickup_location: Mapping[str, Any],
        return_location: Mapping[str, Any],
        pickup_at: str,
        return_at: str,
        driver_age: int,
    ) -> CarRentalResultData:
        body_data = {
            "type": "car-searches",
            "attributes": {
                "pickupLocation": pickup_location,
                "returnLocation": return_location,
                "pickupAt": pickup_at,
                "returnAt": return_at,
                "driverAge": driver_age,
            },
        }

        body = {
            "data": body_data,
        }

        url = "/car-rental/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return CarRentalResultData(result)

    async def get_search_result(self, search_id: str) -> CarRentalResultData:
        result = await self._client.request(
            method=METHOD_GET,
            url="/car-rental/searches/{0}/results".format(search_id),
        )
        return CarRentalResultData(result)

    async def wait_for_search_result(self, search_id: str) -> CarRentalResultData:
        search_status = await poll_until_condition_met(
            request_func=lambda: self._get_search_status(search_id),
            attribute_path="data.attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return CarRentalResultData(search_status)

    async def _get_search_status(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/car-rental/searches/{0}".format(search_id),
        )
