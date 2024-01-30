import asyncio
from collections.abc import AsyncIterator

from snowfall.stdlib.logging import stdout
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import offers, search


class NoResultsError(Exception):
    """Raised when a result page has not results."""


class Adapter(object):
    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        poll_retries_limit: int = 10,
        wait_time_between_polling: float = 2,
    ):
        self._client = ask2go_client
        self._poll_retries_limit = poll_retries_limit
        self._wait_time_between_polling = wait_time_between_polling
        self._logger = stdout.get_logger()

    async def gather_search_results(
        self,
        search_criteria: search.CreateSearchCriteria,
    ) -> AsyncIterator[offers.Offer]:
        identifiers = await self._client.create_search(criteria=search_criteria)

        async for offer in self._gather_offers(identifiers):
            yield offer

    async def _gather_offers(
        self,
        identifiers: search.CreateSearchResponse,
    ) -> AsyncIterator[offers.Offer]:
        async for result_page in self._yield_pages(identifiers=identifiers):
            for offer in result_page.flight:
                offer.search_id = identifiers.id
                yield offer

    async def _yield_pages(
        self,
        identifiers: search.CreateSearchResponse,
    ) -> AsyncIterator[search.SearchResultsResponse]:
        page = 0
        total_pages = 1

        while page < total_pages:
            search_result = await self._get_page(identifiers=identifiers, page=page)
            yield search_result
            total_pages = search_result.page_information.total_pages
            page += 1

    async def _get_page(
        self,
        identifiers: search.CreateSearchResponse,
        page: int,
    ) -> search.SearchResultsResponse:
        for _ in range(self._poll_retries_limit):
            search_result = await self._client.get_search_results(
                search_id=identifiers.id,
                transaction_id=identifiers.transaction_id,
                page_offset=page,
            )

            if search_result.is_finished:
                return search_result

            await asyncio.sleep(self._wait_time_between_polling)

        raise NoResultsError("No results found.")
