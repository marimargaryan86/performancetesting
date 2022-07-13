import asyncio
from collections.abc import AsyncIterator

from snowfall.project.junction.service.providers.ask2go import models, validator
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client, enums
from snowfall.vendor.ask2go import models as ask2go_models


class NoResultsError(Exception):
    """Raised when a result page has not results."""


class Ask2GoAdapter(object):
    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        offer_validator: validator.OfferValidator,
        poll_retries_limit: int = 10,
        wait_time_between_polling: float = 1,
    ):
        self._client = ask2go_client
        self._poll_retries_limit = poll_retries_limit
        self._validator = offer_validator
        self._wait_time_between_polling = wait_time_between_polling

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[ask2go_models.price.OfferPriceResponse]:
        identifiers = await self._make_search(search_task.criteria)
        offer_prices = self._gather_offer_prices(
            identifiers,
            models.requirements_from_segments(search_task.segments),
        )

        async for offer in offer_prices:
            yield offer

    async def _make_search(
        self,
        criteria: amqp_pb2.Criteria,
    ) -> ask2go_models.search.CreateSearchResponse:
        search_criteria = ask2go_models.search.CreateSearchCriteria(
            origin_iata=criteria.origin_iata,
            destination_iata=criteria.destination_iata,
            outbound_date=protobuf.protobuf_to_datetime(criteria.outbound),
            cabin_class=enums.AirCabinClassType(criteria.cabin_class),
            adults=criteria.adults,
            children=criteria.children,
            infants=criteria.infants,
        )

        return await self._client.create_search(criteria=search_criteria)

    async def _gather_offer_prices(
        self,
        identifiers: ask2go_models.search.CreateSearchResponse,
        requirements: models.Requirements,
    ) -> AsyncIterator[ask2go_models.price.OfferPriceResponse]:
        async for result_page in self._yield_pages(identifiers=identifiers):
            for offer in result_page.flight:
                if offer.id and self._validator.matches(offer, requirements):
                    yield await self._client.create_air_offer(
                        search_id=identifiers.id,
                        transaction_id=identifiers.transaction_id,
                        offer_id=offer.id,
                    )

    async def _yield_pages(
        self,
        identifiers: ask2go_models.search.CreateSearchResponse,
    ) -> AsyncIterator[ask2go_models.search.SearchResultsResponse]:
        page = 0
        total_pages = 1

        while page < total_pages:
            search_result = await self._get_page(identifiers=identifiers, page=page)
            yield search_result
            total_pages = search_result.page_information.total_pages
            page += 1

    async def _get_page(
        self,
        identifiers: ask2go_models.search.CreateSearchResponse,
        page: int,
    ) -> ask2go_models.search.SearchResultsResponse:
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
