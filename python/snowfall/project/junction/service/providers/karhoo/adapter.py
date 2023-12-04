import asyncio
import datetime
from collections.abc import AsyncIterator

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
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
        async with asyncio.timeout(self._cut_off):
            async for quote in self._retrieve_quotes(trip.id, passengers_count):
                yield await self._create_offer_group(quote, search_task, trip)

    async def _retrieve_quotes(
        self,
        identity: str,
        passengers_count: int,
    ) -> AsyncIterator[karhoo_quotes.Quote]:
        seen = []
        while True:
            quotes_result = await self._client.list_quotes(
                ident=identity,
                min_passengers=passengers_count,
            )
            for quote in quotes_result.quotes:
                if quote.id not in seen:
                    seen.append(quote.id)
                    yield quote

            if quotes_result.status == _KARHOO_STATUS_COMPLETED:
                break
            await asyncio.sleep(self._wait)

    async def _create_offer_group(
        self,
        quote: karhoo_quotes.Quote,
        search_task: amqp_pb2.Criteria,
        quotes_response: karhoo_quotes.RequestQuotesResponse,
    ) -> offer_models_pb2.OfferGroup:
        expires_at = datetime.datetime.now(datetime.UTC) + self._ttl
        segment = await self._parse_segment(quote, search_task)
        offer = self._parse_offer(quote, segment)
        validity = (
            datetime.timedelta(seconds=quotes_response.validity)
            if (quotes_response.validity and quotes_response.validity > 0)
            else self._ttl
        )
        await self._offers_cache.store(
            cache.OfferDetails(
                quote_id=quote.id,
                quotes_response_id=quotes_response.id,
                expires_at=datetime.datetime.now(datetime.UTC) + validity,
                currency=money.Currency(
                    quote.price.currency_code,
                ),
                price=str(quote.price.high) if quote.price.high else "",
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
            # TODO: Check with Product
            amount=quote.price.high or 0,
            currency=money.Currency(quote.price.currency_code),
        ).protobuf()

        return offer_models_pb2.Offer(
            id=string.uuid(),
            segment_details=[
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=segment.id,
                    cabin_class=models_pb2.CabinClass(
                        # TODO: Check with Product
                        type=models_pb2.CabinClass.TYPE_UNSPECIFIED,
                        marketing_name=quote.vehicle.type if quote.vehicle else "",
                    ),
                ),
            ],
            price=offer_price,
            price_breakdown=[
                offer_models_pb2.PriceBreakdown(
                    price=offer_price,
                    # TODO: Check with product
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
