from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    PlaceData,
)


class PlacesClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def get_place_by_name(self, name: str) -> PlaceData:
        query_parameters = {
            "query[name]": name,
        }
        url = "/places"
        result = await self._client.request(
            method=METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )

        return PlaceData(result)
