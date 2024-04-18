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

    async def get_place_by_place_id(self, place_id: str) -> PlaceData:
        url = "/places/{0}".format(place_id)
        result = await self._client.request(
            method=METHOD_GET,
            url=url,
        )

        return PlaceData(result)
