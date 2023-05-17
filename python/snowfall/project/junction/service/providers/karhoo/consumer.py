import asyncio
import datetime
from typing import AsyncIterator

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.project.junction.service.providers.karhoo import cache
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.karhoo import client, errors
from snowfall.vendor.karhoo.models import location, quotes


class TripOfferSearchConsumer(object):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripOfferSearchTask],
        karhoo_client: client.KarhooClient,
        offers_cache: cache.OffersCache,
        producer_obj: producer.Producer,
        redis: redis_types.Client[bytes],
        ttl: datetime.timedelta,
        polling_wait_time_in_seconds: int,
        polling_retries_attempts: int,
        provider_company_id: str,
    ):
        self._consumer = consumer_obj
        self._client = karhoo_client
        self._offers_cache = offers_cache
        self._producer = producer_obj
        self._redis = redis
        self._ttl = ttl
        self._polling_wait_time = polling_wait_time_in_seconds
        self._polling_retries_attempts = polling_retries_attempts
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[offers_amqp_pb2.TripOfferSearchTask],
    ) -> None:
        trip_offer_groups = self._gather_search_results(message.body)
        async for offer_group in trip_offer_groups:
            await self._producer.publish(
                msg=offers_amqp_pb2.TripOfferSearchResult(
                    offer_search_id=offer_group.id,
                    offer=offer_group,
                    provider_company_id=self._provider_company_id,
                ),
                routing_key="offers.result.trip",
            )

    async def _gather_search_results(
        self,
        trip_offer_search: offers_amqp_pb2.TripOfferSearchTask,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        for trip in trip_offer_search.search.trips:
            for segment in trip.segments:
                leg = segment.legs[0]

                if leg.type != models_pb2.Schedule.TYPE_TAXI:
                    continue
                offer_group_iterator = self._handle_quote_to_offer_group(
                    quote_id=(await self._request_quote(leg)).id,
                    leg=leg,
                    segment=segment,
                )
                async for offer_group in offer_group_iterator:
                    yield offer_group

    async def _request_quote(
        self,
        leg: models_pb2.Leg,
    ) -> quotes.RequestQuotesResponse:
        origin = location.Coordinates(
            latitude=str(leg.origin.coordinates.latitude),
            longitude=str(leg.origin.coordinates.longitude),
            display_address=leg.origin.name,
        )
        destination = location.Coordinates(
            latitude=str(leg.destination.coordinates.latitude),
            longitude=str(leg.destination.coordinates.longitude),
            display_address=leg.destination.name,
        )

        return await self._client.request_quotes(
            origin=origin,
            destination=destination,
            departure_at=protobuf.protobuf_to_datetime(
                leg.departure_at,
            ),
        )

    async def _retrieve_quote_list(
        self,
        quote_id: str,
    ) -> quotes.RequestQuotesResponse:
        return await self._client.list_quotes(ident=quote_id)

    async def _poll_quote_list(
        self,
        quote_id: str,
    ) -> quotes.RequestQuotesResponse:
        for _ in range(self._polling_retries_attempts):
            quote_list = await self._retrieve_quote_list(quote_id)

            if quote_list.status == "COMPLETED":
                return quote_list

            await asyncio.sleep(self._polling_wait_time)

        raise errors.ServiceError(
            "Unable to get quote {0} details, after {1} attempts {2}s apart".format(
                quote_id,
                self._polling_retries_attempts,
                self._polling_wait_time,
            ),
        )

    async def _handle_quote_to_offer_group(
        self,
        quote_id: str,
        leg: models_pb2.Leg,
        segment: models_pb2.Segment,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        quote_list = await self._poll_quote_list(quote_id)

        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        for quote_obj in quote_list.quotes:
            if quote_obj.quote_type != "FIXED":
                continue

            offer_segment_id = string.uuid()
            currency = money.Currency(quote_obj.price.currency_code)

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at),
                offers=[
                    offer_models_pb2.Offer(
                        id=await self._offers_cache.store(
                            cache.OfferDetails(
                                quote_id=quote_obj.id,
                                expires_at=expires_at,
                                price=str(quote_obj.price.high),
                                currency=currency,
                            ),
                        ),
                        segment_details=[
                            offer_models_pb2.OfferSegmentDetails(
                                id=string.uuid(),
                                offer_segment_id=offer_segment_id,
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_UNSPECIFIED,
                                    marketing_name="Unspecified",
                                ),
                            ),
                        ],
                        price=money.from_string(
                            string_amount=str(quote_obj.price.high),
                            currency=currency,
                        ).protobuf(),
                    ),
                ],
                segments=[
                    offer_models_pb2.OfferSegment(
                        id=offer_segment_id,
                        segment_id=segment.id,
                        vendor=quote_obj.fleet.name if quote_obj.fleet.name else "",
                        type=models_pb2.Schedule.TYPE_TAXI,
                        legs=[
                            offer_models_pb2.OfferSegmentLeg(
                                id=leg.id,
                                origin=models_pb2.Point(
                                    ref=leg.origin.ref,
                                    name=leg.origin.name,
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=leg.origin.coordinates.latitude,
                                        longitude=leg.origin.coordinates.longitude,
                                    ),
                                    time_zone=leg.origin.time_zone,
                                ),
                                destination=models_pb2.Point(
                                    ref=leg.destination.ref,
                                    name=leg.destination.name,
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=leg.destination.coordinates.latitude,
                                        longitude=leg.destination.coordinates.longitude,
                                    ),
                                    time_zone=leg.destination.time_zone,
                                ),
                                departure_at=leg.departure_at,
                            ),
                        ],
                    ),
                ],
            )
