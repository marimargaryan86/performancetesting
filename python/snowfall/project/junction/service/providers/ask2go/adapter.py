import asyncio
import datetime
import math
import uuid
from collections.abc import AsyncIterator, Coroutine
from typing import Any, Mapping, Sequence, Tuple

import tenacity

from snowfall.project.junction.service.providers.ask2go import models, validator
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client, enums
from snowfall.vendor.ask2go import errors as ask2go_errors
from snowfall.vendor.ask2go.models import (
    offers,
    price,
    search,
    validate_offer_criteria,
    validated_offer,
)

_BrandedOffersType = Tuple[Sequence[str], Sequence[price.OfferPriceResponse]]
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


class Ask2GoAdapter(object):  # noqa: WPS214
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
    ) -> AsyncIterator[_BrandedOffersType]:
        identifiers = await self._make_search(search_task)
        branded_prices = self._gather_offer_branded_prices(
            identifiers,
            models.requirements_from_segments(search_task.segments),
            search_task.criteria,
        )

        async for branded_prices_item in branded_prices:
            yield branded_prices_item

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

    async def _gather_offer_branded_prices(
        self,
        identifiers: search.CreateSearchResponse,
        requirements: models.Requirements,
        criteria: amqp_pb2.Criteria,
    ) -> AsyncIterator[_BrandedOffersType]:
        async for result_page in self._yield_pages(identifiers=identifiers):
            for offer in result_page.flight:
                if offer.id and self._validator.matches(offer, requirements):
                    validate_identifiers = await self._get_offer_validate(
                        identifiers,
                        offer,
                        criteria,
                    )
                    branded_offer = await self._get_branded_offer(validate_identifiers)
                    mapped_brand_price = await self._get_mapped_brand_price(
                        offer,
                        identifiers,
                        validate_identifiers,
                        branded_offer,
                    )

                    yield await self._merge_brands_prices(
                        list(mapped_brand_price.keys()),
                        list(mapped_brand_price.values()),
                    )

    async def _get_mapped_brand_price(
        self,
        offer: offers.Offer,
        identifiers: search.CreateSearchResponse,
        validate_identifiers: validate_offer_criteria.ValidateOfferResponse,
        branded_offer: validated_offer.ValidatedOfferResponse,
    ) -> Mapping[str, Coroutine[price.OfferPriceResponse, Any, Any]]:
        mapped_brand_price = {}
        if branded_offer.itinerary.branded_fares:
            mapped_brand_price.update(
                {
                    fare.brand_name: await self._get_async_price(
                        search_id=validate_identifiers.identifier,
                        transaction_id=identifiers.transaction_id,
                        offer_id=offer.id,
                        brand_id=fare.brand_id,
                    )
                    for fare in branded_offer.itinerary.branded_fares
                },
            )
        else:
            mapped_brand_price["BASIC FARE"] = await self._get_async_price(
                search_id=validate_identifiers.identifier,
                transaction_id=identifiers.transaction_id,
                offer_id=offer.id,
            )

        return mapped_brand_price

    async def _get_async_price(
        self,
        transaction_id: str,
        search_id: str,
        offer_id: str,
        brand_id: str | None = None,
    ) -> Coroutine[price.OfferPriceResponse, Any, Any]:
        async_offer = await self._client.create_air_offer_async(
            search_id=search_id,
            transaction_id=transaction_id,
            offer_id=offer_id,
            brand_id=brand_id,
        )

        return self._get_async_price_result(async_offer)

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(ask2go_errors.TimeOutError),
        wait=tenacity.wait_random_exponential(multiplier=1, max=5),
    )
    async def _get_async_price_result(
        self,
        async_offer: price.AsyncOfferPriceResponse,
    ) -> price.OfferPriceResponse:
        return await self._client.get_air_offer_result(
            transaction_id=async_offer.transaction_id,
            pricing_id=async_offer.id,
        )

    async def _merge_brands_prices(
        self,
        fare_brands: Sequence[str],
        coroutines: Sequence[Coroutine[price.OfferPriceResponse, Any, Any]],
    ) -> _BrandedOffersType:
        return (
            fare_brands,
            await asyncio.gather(*coroutines),
        )

    async def _get_offer_validate(
        self,
        identifiers: search.CreateSearchResponse,
        offer: offers.Offer,
        criteria: amqp_pb2.Criteria,
    ) -> validate_offer_criteria.ValidateOfferResponse:
        return await self._client.validate_offer(
            criteria=validate_offer_criteria.ValidateOfferCriteria(
                transaction_id=identifiers.transaction_id,
                currency="EUR",
                flight_segments=[
                    validate_offer_criteria.SegmentCriteria(
                        trip_number=trip_index,
                        segment_number=segment_index,
                        flight_number=segment.aircraft.flight_number,
                        departure_date=segment.departure.date_time,
                        arrival_date=segment.arrival.date_time,
                        origin_iata=segment.origin.airport_code,
                        destination_iata=segment.destination.airport_code,
                        marketing_airline=segment.marketing_carrier.code,
                        operating_airline=segment.operating_carrier.code,
                        equipment=segment.aircraft.equipment,
                    )
                    for trip_index, trip in enumerate(offer.trips)
                    for segment_index, segment in enumerate(trip.segments)
                ],
                passengers=self._get_offer_validate_passengers(criteria),
            ),
        )

    def _get_offer_validate_passengers(
        self,
        criteria: amqp_pb2.Criteria,
    ) -> list[validate_offer_criteria.PassengerCriteria]:
        passengers = []

        if criteria.adults:
            passengers.append(
                validate_offer_criteria.PassengerCriteria(
                    code=enums.PassengerType.adult,
                    count=criteria.adults,
                ),
            )
        if criteria.children:
            passengers.append(
                validate_offer_criteria.PassengerCriteria(
                    code=enums.PassengerType.child,
                    count=criteria.children,
                ),
            )
        if criteria.infants:
            passengers.append(
                validate_offer_criteria.PassengerCriteria(
                    code=enums.PassengerType.infant,
                    count=criteria.infants,
                ),
            )

        return passengers

    async def _get_branded_offer(
        self,
        validate_identifiers: validate_offer_criteria.ValidateOfferResponse,
    ) -> validated_offer.ValidatedOfferResponse:
        retry = tenacity.Retrying(
            retry=tenacity.retry_if_exception_type(ask2go_errors.AcceptedResponseError),
            wait=tenacity.wait_random_exponential(multiplier=1, max=5),
        )
        for attempt in retry:
            with attempt:
                branded_offer = await self._client.get_validated_offer(
                    pricing_id=validate_identifiers.identifier,
                    transaction_id=validate_identifiers.transaction_id,
                )

        return branded_offer

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
