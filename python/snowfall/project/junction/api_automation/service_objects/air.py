from collections.abc import Sequence
from datetime import date

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    AirResultData,
)


class AirClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        origin: str,
        destination: str,
        departure_after: str,
        passengers_dates_of_birth: Sequence[date],
    ) -> AirResultData:
        criteria = {
            "origin": origin,
            "destination": destination,
            "departureAt": departure_after,
        }

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

        return AirResultData(result)
