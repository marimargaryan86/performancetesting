from itertools import starmap

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    PlaceData,
    PlaceListData,
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

        return PlaceData(result["data"])

    async def get_place_list(
        self,
        name_like: str | None = None,
        type_eq: str | None = None,
        iata_eq: str | None = None,
        coordinates: str | None = None,
        place_to_search_within: str | None = None,
        page_limit: int | None = None,
    ) -> PlaceListData:
        params = {}
        if name_like is not None:
            params["filter[name][like]"] = name_like
        if type_eq is not None:
            params["filter[type][eq]"] = type_eq
        if iata_eq is not None:
            params["filter[iata][eq]"] = iata_eq
        if coordinates is not None:
            params["query[coordinates]"] = coordinates
        if place_to_search_within is not None:
            params["query[placeToSearchWithin]"] = place_to_search_within
        if page_limit is not None:
            params["page[limit]"] = str(page_limit)

        url = "/places"
        if params:
            query_string = "&".join(list(starmap("{0}={1}".format, params.items())))
            url = "{0}?{1}".format(url, query_string)
        result = await self._client.request(method=METHOD_GET, url=url)
        return PlaceListData(result)

    async def get_place_by_next_link(self, url: str) -> PlaceListData:
        result = await self._client.request(
            method=METHOD_GET,
            url=url,
        )
        return PlaceListData(result)
