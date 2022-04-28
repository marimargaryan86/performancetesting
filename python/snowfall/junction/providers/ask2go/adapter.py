import asyncio
import datetime
import uuid
from collections.abc import AsyncIterator

import more_itertools

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.junction.providers.ask2go import airports, cache, models
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client, enums
from snowfall.vendor.ask2go import models as ask2go_models


class NoResultsError(Exception):
    """Raised when a result page has not results."""


def offer_matches_requirements(
    offer: ask2go_models.offers.Offer,
    requirements: models.Requirements,
) -> bool:
    last_index = 0

    for trip in offer.trips:
        for segment_index, segment in enumerate(trip.segments, start=last_index):
            try:
                if not segment_in_requirements(segment, requirements[segment_index]):
                    return False
            except IndexError:
                return False

            last_index = segment_index

    return True


def segment_in_requirements(
    segment: ask2go_models.offers.TripSegment,
    requirement: models.Requirement,
) -> bool:
    departure_at = segment.departure.date_time.replace(tzinfo=requirement.departure_tz)

    if departure_at != requirement.departure_at:
        return False

    arrival_at = segment.arrival.date_time.replace(tzinfo=requirement.arrival_tz)

    return arrival_at == requirement.arrival_at


class Ask2GoAdapter(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 1

    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        airport_repository: airports.AirportRepository,
        offer_cache: cache.OfferCache,
        ttl: datetime.timedelta,
    ):
        self._airports = airport_repository
        self._cache = offer_cache
        self._client = ask2go_client
        self._ttl = ttl

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        identifiers = await self._make_search(search_task.criteria)
        offer_prices = self._offer_prices_to_offers(
            search_task=search_task,
            offer_prices=self._gather_offer_prices(
                identifiers,
                models.requirements_from_segments(search_task.segments),
            ),
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
            outbound_date=protobuf.protobuf_to_date(criteria.outbound),
            cabin_class=enums.AirCabinClassType(criteria.cabin_class),
            adults=criteria.adults,
            children=criteria.children,
            infants=criteria.infants,
        )

        return await self._client.create_search(criteria=search_criteria)

    async def _offer_prices_to_offers(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_prices: AsyncIterator[ask2go_models.price.OfferPriceResponse],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        async for offer_price in offer_prices:
            segment = more_itertools.first(
                more_itertools.first(offer_price.itinerary.trips).segments,
            )
            search_segment = more_itertools.first(search_task.segments)
            origin = self._airports.get_by_iata(segment.origin.airport_code)
            destination = self._airports.get_by_iata(segment.destination.airport_code)

            yield offers_pb2.OfferGroup(
                id=str(uuid.uuid4()),
                offer_search_id=search_task.offer_search_id,
                expires_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
                ),
                offers=[
                    offers_pb2.Offer(
                        id=await self._cache.store(
                            pricing_id=offer_price.id,
                            transaction_id=offer_price.transaction_id,
                        ),
                        segment_details=[
                            offers_pb2.OfferSegmentDetails(
                                id=search_segment.id,
                                cabin_class=models_pb2.CabinClass(
                                    type=models.cabin_to_proto(segment.cabin),
                                    marketing_name=segment.cabin,
                                ),
                            ),
                        ],
                        price=models_pb2.Price(
                            amount=int(
                                offer_price.itinerary.pricing_information.base.total_cost
                                * 100,
                            ),
                            currency=offer_price.itinerary.pricing_information.base.currency,
                        ),
                    ),
                ],
                segments=[
                    offers_pb2.OfferSegment(
                        id=search_segment.id,
                        legs=[
                            offers_pb2.OfferSegmentLeg(
                                id=search_segment.legs[0].id,
                                origin=models_pb2.Point(
                                    ref=origin.iata,
                                    name=str(origin.airport_name),
                                    coordinates=models_pb2.Coordinates(
                                        latitude=origin.latitude,
                                        longitude=origin.longitude,
                                    ),
                                    time_zone=origin.timezone.key,
                                ),
                                destination=models_pb2.Point(
                                    ref=destination.iata,
                                    name=str(destination.airport_name),
                                    coordinates=models_pb2.Coordinates(
                                        latitude=destination.latitude,
                                        longitude=destination.longitude,
                                    ),
                                    time_zone=destination.timezone.key,
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    segment.departure.date_time.replace(
                                        tzinfo=origin.timezone,
                                    ),
                                ),
                                arrival_at=protobuf.datetime_to_protobuf(
                                    segment.arrival.date_time.replace(
                                        tzinfo=destination.timezone,
                                    ),
                                ),
                            ),
                        ],
                        vehicle=offers_pb2.Vehicle(
                            equipment=segment.aircraft.equipment,
                            number=segment.aircraft.flight_number,
                        ),
                        operator=segment.operating_carrier.code,
                        vendor=segment.marketing_carrier.code,
                        terminal=str(segment.origin_terminal),
                    ),
                ],
            )

    async def _gather_offer_prices(
        self,
        identifiers: ask2go_models.search.CreateSearchResponse,
        requirements: models.Requirements,
    ) -> AsyncIterator[ask2go_models.price.OfferPriceResponse]:
        async for result_page in self._yield_pages(identifiers=identifiers):
            for offer in result_page.flight:
                if offer.id and offer_matches_requirements(offer, requirements):
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
