from typing import Any, Callable, Optional

import httpx

from snowfall.providers.ask2go import errors, parsers
from snowfall.providers.ask2go.models import search


class Ask2GoClient(object):
    def __init__(
        self,
        api_base_url: str,
        http_client: httpx.Client,
    ) -> None:
        self._api_base_url = api_base_url
        self._http_client = http_client

    async def create_search(
        self,
        criteria: search.CreateSearchCriteria,
    ) -> search.CreateSearchResponse:
        if criteria.inbound_date and criteria.inbound_date < criteria.outbound_date:
            raise errors.DateError(
                "Inbound date must be after outbound date, "
                + "{inbound_date} is lower than {outbound_date}".format(
                    outbound_date=criteria.outbound_date,
                    inbound_date=criteria.inbound_date,
                ),
            )

        resp = self._http_client.post(
            "{api_base_url}/search".format(api_base_url=self._api_base_url),
            json=parsers.parse_search_request(criteria),
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        return search.CreateSearchResponse(**resp.json())

    async def get_search_results(
        self,
        transaction_id: str,
        search_id: str,
        page_offset: int,
    ) -> search.SearchResultsResponse:
        search_res = await self._poll(
            "{api_base_url}/search/{search_id}/{transaction_id}/{page_offset}".format(
                api_base_url=self._api_base_url,
                search_id=search_id,
                transaction_id=transaction_id,
                page_offset=page_offset,
            ),
            None,
            lambda search_data: search_data["isFinished"],
        )

        return search.SearchResultsResponse(**search_res)

    async def _poll(
        self,
        request_url: str,
        query_params: Optional[dict[str, Any]],
        validator: Callable[[dict[str, Any]], bool],
    ) -> dict[str, Any]:
        resp = self._http_client.get(request_url, params=query_params)

        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError() from exc

        json_data = resp.json()

        if validator(json_data):
            return json_data

        raise errors.ServiceError()
