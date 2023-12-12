import asyncio
import datetime
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from types import MappingProxyType
from typing import NamedTuple

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.service.providers.karhoo import (
    cache,
    constant,
    helper_functions,
)
from snowfall.project.junction.service.providers.karhoo.v1 import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.karhoo import client
from snowfall.vendor.karhoo.models import location
from snowfall.vendor.karhoo.models import quotes as karhoo_quotes

_KARHOO_STATUS_PROGRESSING = "PROGRESSING"
_KARHOO_STATUS_COMPLETED = "COMPLETED"
_QUOTE_TYPE_FIXED = "FIXED"
_KARHOO_CABIN_CLASSES: MappingProxyType[
    str,
    common_pb2.CabinClass.Type.ValueType,
] = MappingProxyType(
    {
        "luxury": common_pb2.CabinClass.TYPE_PREMIUM,
        "executive": common_pb2.CabinClass.TYPE_BUSINESS,
        "electric": common_pb2.CabinClass.TYPE_ECONOMY,
        "hybrid": common_pb2.CabinClass.TYPE_ECONOMY,
    },
)


def _get_cabin_class_from_tags(
    tags: Sequence[str],
) -> common_pb2.CabinClass.Type.ValueType:
    target_tags = _KARHOO_CABIN_CLASSES.keys()

    for tag in target_tags:
        if tag in tags:
            return _KARHOO_CABIN_CLASSES[tag]

    return common_pb2.CabinClass.TYPE_UNSPECIFIED


async def _retrieve_quotes(  # noqa: WPS231
    list_quotes: Callable[[str, int], Awaitable[karhoo_quotes.RequestQuotesResponse]],
    identity: str,
    passengers_count: int,
    wait: int,
) -> AsyncIterator[karhoo_quotes.Quote]:
    seen = []
    while True:
        quotes_result = await list_quotes(
            identity,
            passengers_count,
        )
        for quote in quotes_result.quotes:
            if quote.quote_type != _QUOTE_TYPE_FIXED:
                continue
            if quote.id not in seen:
                seen.append(quote.id)
                yield quote

        if quotes_result.status == _KARHOO_STATUS_COMPLETED:
            break
        await asyncio.sleep(wait)


class QuoteResult(NamedTuple):
    quote: karhoo_quotes.Quote
    quotes_response: karhoo_quotes.RequestQuotesResponse


class KarhooOfferMatcher(object):
    def __init__(self, karhoo_client: client.KarhooClient, ttl: datetime.timedelta):
        self._karhoo_client = karhoo_client
        self._wait = 1
        self._cut_off = 30
        self._ttl = ttl

    async def get_matching_quote(
        self,
        offer_details: cache.OfferDetails,
    ) -> QuoteResult | None:
        quotes_response = await self._karhoo_client.request_quotes(
            origin=location.Coordinates(
                latitude=str(offer_details.origin.latitude),
                longitude=str(offer_details.origin.longitude),
            ),
            destination=location.Coordinates(
                latitude=str(offer_details.destination.latitude),
                longitude=str(offer_details.destination.longitude),
            ),
            departure_at=offer_details.departure_at,
        )

        quotes = _retrieve_quotes(
            self._karhoo_client.list_quotes,
            quotes_response.id,
            offer_details.passengers_count,
            self._wait,
        )

        async with asyncio.timeout(self._cut_off):
            async for quote in quotes:
                if self._offer_matches(quote, offer_details):
                    return QuoteResult(quote, quotes_response)

        return None

    def _offer_matches(
        self,
        quote: karhoo_quotes.Quote,
        offer_details: cache.OfferDetails,
    ) -> bool:
        cabin_class = cache.CabinClass(
            type=int(
                _get_cabin_class_from_tags(
                    quote.vehicle.tags if quote.vehicle else [],
                ),
            ),
            marketing_name=quote.vehicle.type if quote.vehicle else "",
        )
        return cabin_class == offer_details.cabin_class


class KarhooOffersAdapter(object):
    def __init__(
        self,
        karhoo_client: client.KarhooClient,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ):
        self._client = karhoo_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = stdout.get_logger()
        self._wait = 1
        self._cut_off = 30

    async def gather_offer_groups(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        try:
            async for offer_group in self._gather_offer_groups(search_task):
                yield offer_group
        except errors.HttpError:
            self._logger.exception("Offer search failed")

    async def _gather_offer_groups(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        trip = await self._client.request_quotes(
            origin=location.Coordinates(
                latitude=str(search_task.origin.latitude),
                longitude=str(search_task.origin.longitude),
            ),
            destination=location.Coordinates(
                latitude=str(search_task.destination.latitude),
                longitude=str(search_task.destination.longitude),
            ),
            departure_at=protobuf.protobuf_to_datetime(
                search_task.departure_datetime,
            ),
        )
        passengers_count = search_task.passengers_count
        quotes = _retrieve_quotes(
            self._client.list_quotes,
            trip.id,
            passengers_count,
            self._wait,
        )
        async with asyncio.timeout(self._cut_off):
            async for quote in quotes:
                yield await self._create_offer_group(quote, search_task)

    async def _create_offer_group(
        self,
        quote: karhoo_quotes.Quote,
        search_task: amqp_pb2.Criteria,
    ) -> offer_models_pb2.OfferGroup:
        expires_at = datetime.datetime.now(datetime.UTC) + self._ttl
        segment = await self._parse_segment(quote, search_task)
        offer = self._parse_offer(quote, segment)
        await self._offers_cache.store(
            cache.OfferDetails(
                currency=money.Currency(
                    quote.price.currency_code,
                ),
                price=str(quote.price.high) if quote.price.high else "",
                origin=cache.Coordinates(
                    latitude=search_task.origin.latitude,
                    longitude=search_task.origin.longitude,
                ),
                destination=cache.Coordinates(
                    latitude=search_task.destination.latitude,
                    longitude=search_task.destination.longitude,
                ),
                passengers_count=search_task.passengers_count,
                cabin_class=cache.CabinClass(
                    type=int(offer.segment_details[0].cabin_class.type),
                    marketing_name=offer.segment_details[0].cabin_class.marketing_name,
                ),
                departure_at=protobuf.protobuf_to_datetime(
                    search_task.departure_datetime,
                ),
            ),
            expires_at=expires_at,
            key=offer.id,
        )
        return offer_models_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[offer],
            segments=[segment],
            provider_id=str(constant.PROVIDER_ID),
        )

    def _parse_offer(
        self,
        quote: karhoo_quotes.Quote,
        segment: offer_models_pb2.OfferSegment,
    ) -> offer_models_pb2.Offer:
        offer_price = money.Money(
            amount=quote.price.high or 0,
            currency=money.Currency(quote.price.currency_code),
        ).protobuf()

        is_baggage_free = True
        if quote.vehicle and quote.vehicle.luggage_capacity == 0:
            is_baggage_free = False

        return offer_models_pb2.Offer(
            id=string.uuid(),
            segment_details=[
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=segment.id,
                    cabin_class=models_pb2.CabinClass(
                        type=_get_cabin_class_from_tags(
                            quote.vehicle.tags if quote.vehicle else [],
                        ),
                        marketing_name=quote.vehicle.type if quote.vehicle else "",
                    ),
                    baggage_allowances=[
                        offer_models_pb2.BaggageAllowance(
                            free=is_baggage_free,
                        ),
                    ],
                ),
            ],
            price=offer_price,
            price_breakdown=[
                offer_models_pb2.PriceBreakdown(
                    price=offer_price,
                    breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
            brand_name=quote.quote_type.title(),
        )

    async def _parse_segment(
        self,
        quote: karhoo_quotes.Quote,
        search_task: amqp_pb2.Criteria,
    ) -> offer_models_pb2.OfferSegment:
        leg = self._get_leg(search_task)
        return offer_models_pb2.OfferSegment(
            id=string.uuid(),
            legs=[leg],
            vehicle=offer_models_pb2.Vehicle(
                equipment=quote.vehicle.type if quote.vehicle else "",
            ),
            vendor=quote.fleet.name,
            type=models_pb2.Schedule.TYPE_TAXI,
        )

    def _get_leg(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> offer_models_pb2.OfferSegmentLeg:
        return offer_models_pb2.OfferSegmentLeg(
            id=string.uuid(),
            origin=models_pb2.Point(
                name="",
                coordinates=search_task.origin,
                time_zone=helper_functions.get_zone_for_coordinate(
                    coordinate=search_task.origin,
                ).key,
            ),
            destination=models_pb2.Point(
                name="",
                coordinates=search_task.destination,
                time_zone=helper_functions.get_zone_for_coordinate(
                    coordinate=search_task.destination,
                ).key,
            ),
            departure_at=protobuf.datetime_to_protobuf(
                protobuf.protobuf_to_datetime(search_task.departure_datetime),
            ),
        )
