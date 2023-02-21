import datetime
from collections import defaultdict
from typing import AbstractSet, AsyncIterator, Callable, List, Mapping, Sequence

import structlog

from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.duffel import cache
from snowfall.project.junction.service.providers.duffel.search.parser import OfferParser
from snowfall.project.junction.service.providers.duffel.search.validator import (
    AirlineValidator,
    Validators,
)
from snowfall.project.junction.service.providers.duffel.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders.offer_request import (
    OfferRequestData,
    OfferRequestPassenger,
    OfferRequestSlice,
    OffersRequestBuilder,
)
from snowfall.vendor.duffel.models.offer import Offer
from snowfall.vendor.duffel.models.offer_slice import OfferSliceSegment


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                *[segment.id for segment in task.segments],
                *[str(age) for age in task.criteria.passenger_ages],
                task.criteria.origin_iata,
                task.criteria.destination_iata,
            ],
        ),
    )


class OfferGrouper(object):
    @classmethod
    def group_offers(
        cls,
        offers: Sequence[Offer],
        validator: Callable[[Offer], bool],
    ) -> Mapping[str, List[Offer]]:
        offer_groups = defaultdict[str, list[Offer]](list)

        for offer in offers or []:
            if validator(offer):
                offer_groups[cls._offer_key(offer)].append(offer)

        return offer_groups

    @classmethod
    def _segment_key(cls, segment: OfferSliceSegment) -> str:
        return "".join(
            [
                segment.arriving_at.isoformat(),
                segment.departing_at.isoformat(),
                segment.origin.iata_code or "",
                segment.destination.iata_code or "",
                segment.marketing_carrier.iata_code or "",
                segment.operating_carrier.iata_code or "",
                segment.marketing_carrier_flight_number,
            ],
        )

    @classmethod
    def _offer_key(cls, offer: Offer) -> str:
        return "|".join(
            cls._segment_key(segment)
            for offer_slice in offer.slices
            for segment in offer_slice.segments
        )


class DuffelSearchAdapter(object):
    def __init__(  # noqa: WPS211
        self,
        duffel_client: client.DuffelClient,
        offers_cache: cache.OfferCache,
        ttl: datetime.timedelta,
        enabled_airlines: AbstractSet[str] | None = None,
        disabled_airlines: AbstractSet[str] | None = None,
    ) -> None:
        self._client = duffel_client
        self._offer_parser = OfferParser(default_ttl=ttl, offer_cache=offers_cache)
        self._logger = structlog.get_logger(__name__)
        self._airline_validator = AirlineValidator(
            enabled_airlines=enabled_airlines,
            disabled_airlines=disabled_airlines,
        )

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        res = await self._client.create_offer_request(
            self._build_search_request(search_task),
        )

        if res.offers:
            validator = Validators(
                self._airline_validator,
            )
            grouped_offers = OfferGrouper.group_offers(res.offers, validator.matches)

            for offers in grouped_offers.values():
                offer_group = await self._offer_parser.parse_offer_group(
                    offers,
                )

                if offer_group:
                    yield offer_group

    def _build_search_request(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> OfferRequestData:
        offer_request_builder = OffersRequestBuilder()
        outbound_date = protobuf.protobuf_to_datetime(
            search_task.criteria.outbound_departure,
        )

        for passenger_age in search_task.criteria.passenger_ages:
            offer_request_builder.add_passenger(
                OfferRequestPassenger(age=passenger_age, pax_type=None),
            )

        offer_request_builder.add_slice(
            OfferRequestSlice(
                destination=search_task.criteria.destination_iata,
                origin=search_task.criteria.origin_iata,
                departure_date=outbound_date,
            ),
        )

        if search_task.criteria.HasField("inbound_departure"):
            inbound_date = protobuf.protobuf_to_datetime(
                search_task.criteria.inbound_departure,
            )
            offer_request_builder.add_slice(
                OfferRequestSlice(
                    destination=search_task.criteria.origin_iata,
                    origin=search_task.criteria.destination_iata,
                    departure_date=inbound_date,
                ),
            )

        return offer_request_builder.build()
