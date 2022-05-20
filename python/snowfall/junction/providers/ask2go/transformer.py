import datetime
import uuid
from collections.abc import AsyncIterator

import more_itertools

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.junction.providers.ask2go import airports, cache, models
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import models as ask2go_models


class OfferTransformer(object):
    def __init__(
        self,
        airport_repository: airports.AirportRepository,
        offer_cache: cache.OfferCache,
        offer_ttl: datetime.timedelta,
    ):
        self._airports = airport_repository
        self._cache = offer_cache
        self._ttl = offer_ttl

    async def offer_prices_to_offer_groups(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_prices: AsyncIterator[ask2go_models.price.OfferPriceResponse],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        async for offer_price in offer_prices:
            yield await self._offer_price_to_offer_group(search_task, offer_price)

    async def _offer_price_to_offer_group(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_price: ask2go_models.price.OfferPriceResponse,
    ) -> offers_pb2.OfferGroup:
        segment = more_itertools.first(
            more_itertools.first(offer_price.itinerary.trips).segments,
        )
        search_segment = more_itertools.first(search_task.segments)
        origin = self._airports.get_by_iata(segment.origin.airport_code)
        destination = self._airports.get_by_iata(segment.destination.airport_code)
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        return offers_pb2.OfferGroup(
            id=str(uuid.uuid4()),
            offer_search_id=search_task.offer_search_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=[
                offers_pb2.Offer(
                    id=await self._cache.store(
                        pricing_id=offer_price.id,
                        transaction_id=offer_price.transaction_id,
                        expires_at=expires_at,
                    ),
                    segment_details=[
                        offers_pb2.OfferSegmentDetails(
                            id=search_segment.id,
                            cabin_class=models_pb2.CabinClass(
                                type=models.cabin_to_proto(segment.cabin),
                                marketing_name=str(segment.cabin),
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
