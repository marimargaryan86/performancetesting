import asyncio
import datetime
import math
import uuid
from collections.abc import AsyncIterator

import structlog

from snowfall.project.junction.service.providers.ask2go import models, validator
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client, enums
from snowfall.vendor.ask2go.models import offers, search

_WINDOW_SIZE = 6


def time_to_window(
    departure_time: datetime.time,
) -> tuple[datetime.time, datetime.time]:
    lower_bound_multiplier = math.floor(departure_time.hour / _WINDOW_SIZE)
    earliest_hour = _WINDOW_SIZE * lower_bound_multiplier
    latest_hour = _WINDOW_SIZE * (lower_bound_multiplier + 1)

    if latest_hour == 24:
        latest_hour = 0

    return (
        datetime.time(hour=earliest_hour),
        datetime.time(hour=latest_hour),
    )


class NoResultsError(Exception):
    """Raised when a result page has not results."""


class Adapter(object):
    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        offer_validator: validator.OfferValidator,
        poll_retries_limit: int = 10,
        wait_time_between_polling: float = 2,
    ):
        self._client = ask2go_client
        self._poll_retries_limit = poll_retries_limit
        self._validator = offer_validator
        self._wait_time_between_polling = wait_time_between_polling
        self._logger = structlog.get_logger(__name__)

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offers.Offer]:
        identifiers = await self._make_search(search_task)
        requirements = models.requirements_from_segments(search_task.segments)

        async for offer in self._gather_offers(identifiers, requirements):
            yield offer

    async def _make_search(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> search.CreateSearchResponse:
        outbound_date = protobuf.protobuf_to_datetime(
            search_task.criteria.outbound_departure,
        )
        search_criteria = search.CreateSearchCriteria(
            transaction_id=uuid.UUID(string.to_uuid(search_task.session_token)),
            origin_iata=search_task.criteria.origin_iata,
            destination_iata=search_task.criteria.destination_iata,
            outbound_date=outbound_date.date(),
            outbound_departure_window=time_to_window(outbound_date.time()),
            cabin_class=enums.AirCabinClassType(search_task.criteria.cabin_class),
            adults=search_task.criteria.adults,
            children=search_task.criteria.children,
            infants=search_task.criteria.infants,
        )

        if search_task.criteria.HasField("inbound_departure"):
            inbound_date = protobuf.protobuf_to_datetime(
                search_task.criteria.inbound_departure,
            )
            search_criteria.inbound_date = inbound_date.date()
            search_criteria.inbound_departure_window = time_to_window(
                inbound_date.time(),
            )

        return await self._client.create_search(criteria=search_criteria)

    async def _gather_offers(
        self,
        identifiers: search.CreateSearchResponse,
        requirements: models.Requirements,
    ) -> AsyncIterator[offers.Offer]:
        async for result_page in self._yield_pages(identifiers=identifiers):
            for offer in result_page.flight:
                if offer.id and self._validator.matches(offer, requirements):
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
