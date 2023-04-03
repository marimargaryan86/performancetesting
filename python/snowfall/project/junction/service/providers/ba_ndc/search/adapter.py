from collections import defaultdict
from typing import AsyncIterator, Mapping

import structlog

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.provider import airports
from snowfall.project.junction.service.providers.ba_ndc import cache
from snowfall.project.junction.service.providers.ba_ndc.search import parser
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.builders.offer_request import OffersRequestBuilder
from snowfall.vendor.ba_ndc.models import (
    request_offer_search_schemas,
    response_common_offer_schemas,
    response_offer_search_schemas,
)
from snowfall.vendor.ba_ndc.models.util import offer_enums, passenger_enums


class OfferGrouper(object):
    @classmethod
    def group_offers(
        cls,
        offers_adapter: OffersResponseAdapter,
    ) -> Mapping[str, list[response_offer_search_schemas.Offer]]:
        offer_groups = defaultdict[str, list[response_offer_search_schemas.Offer]](list)

        for offer in offers_adapter.get_offers() or []:
            offer_groups[cls._offer_key(offer, offers_adapter)].append(offer)

        return offer_groups

    @classmethod
    def _segment_key(cls, segment: response_common_offer_schemas.Segment | None) -> str:
        if segment:
            return "".join(
                [
                    segment.arrival_date_time.isoformat(),
                    segment.departure_date_time.isoformat(),
                    segment.origin.code or "",
                    segment.destination.code or "",
                    segment.marketing_carrier.airline_id or "",
                    (
                        segment.operating_carrier.airline_id
                        if segment.operating_carrier
                        else ""
                    ),
                    segment.marketing_carrier.flight_number or "",
                ],
            )

        return ""

    @classmethod
    def _offer_key(
        cls,
        offer: response_offer_search_schemas.Offer,
        offers_adapter: OffersResponseAdapter,
    ) -> str:
        return "|".join(
            cls._segment_key(offers_adapter.get_segment_by_id(segment))
            for trip in offer.trips
            for segment in trip.segment_ids
        )


class BaNdcSearchAdapter(object):
    def __init__(
        self,
        ba_ndc_client: client.BaNdcClient,
        airport_repository: airports.AirportRepository,
        offers_cache: cache.OfferCache,
    ) -> None:
        self._client = ba_ndc_client
        self._offer_parser = parser.OfferParser(
            offer_cache=offers_cache,
            airport_repository=airport_repository,
        )
        self._logger = structlog.get_logger(__name__)

    def search_criteria_generator(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> request_offer_search_schemas.OfferSearchRequest:
        offer_request_builder = OffersRequestBuilder()
        outbound_date = protobuf.protobuf_to_datetime(
            search_task.criteria.outbound_departure,
        )

        for _ in range(search_task.criteria.adults):
            offer_request_builder.add_passenger(passenger_enums.PassengerTypeEnum.adult)

        for _ in range(search_task.criteria.children):
            offer_request_builder.add_passenger(passenger_enums.PassengerTypeEnum.child)

        for _ in range(search_task.criteria.infants):
            offer_request_builder.add_passenger(
                passenger_enums.PassengerTypeEnum.infant,
            )

        if search_task.criteria.cabin_class:
            offer_request_builder.set_cabin(
                offer_enums.CabinTypeEnum(search_task.criteria.cabin_class),
            )

        offer_request_builder.add_trip(
            request_offer_search_schemas.Trip(
                destination=search_task.criteria.destination_iata,
                origin=search_task.criteria.origin_iata,
                date=outbound_date.date(),
                time=outbound_date.time(),
            ),
        )

        if search_task.criteria.HasField("inbound_departure"):
            inbound_date = protobuf.protobuf_to_datetime(
                search_task.criteria.inbound_departure,
            )
            offer_request_builder.add_trip(
                request_offer_search_schemas.Trip(
                    destination=search_task.criteria.origin_iata,
                    origin=search_task.criteria.destination_iata,
                    date=inbound_date.date(),
                    time=inbound_date.time(),
                ),
            )

        return offer_request_builder.build()

    def generate_cache_key(
        self,
        search_criteria: request_offer_search_schemas.OfferSearchRequest,
    ) -> str:
        return string.to_uuid(
            b"\x00".decode().join(
                [
                    search_criteria.cabin_type.name,
                    str(search_criteria.fare_preferences),
                    *[
                        "{origin}-{destination}-{date}-{time}".format(
                            origin=trip.origin,
                            destination=trip.destination,
                            date=trip.date,
                            time=trip.time,
                        )
                        for trip in search_criteria.trips
                    ],
                    *[
                        passenger.passenger_type.name
                        for passenger in search_criteria.passengers
                    ],
                ],
            ),
        )

    async def gather_search_results(
        self,
        search_criteria: request_offer_search_schemas.OfferSearchRequest,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        res = await self._client.get_offers(search_criteria)

        if res.get_offers():
            grouped_offers = OfferGrouper.group_offers(res)

            for offers in grouped_offers.values():
                offer_group = await self._offer_parser.parse_offer_group(
                    offers,
                    res,
                )

                if offer_group:
                    yield offer_group
