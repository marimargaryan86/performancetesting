import asyncio
import datetime

from snowfall.project.junction.go.service.offers.offers import OfferOptionsRepository
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2, models_pb2
from snowfall.stdlib.transport.amqp import protocol, trackable


class OfferSearchProducer:
    def __init__(
        self,
        producer: trackable.TrackableProducer | protocol.Producer,
        routing_key: str,
        ttl: datetime.timedelta | None = None,
    ):
        self._producer = producer
        self._routing_key = routing_key
        self._ttl = ttl

    async def publish(
        self,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        msg: amqp_pb2.TripOfferSearchTask | amqp_pb2.SimpleTripOfferSearchTask
        if offer_search.HasField("simple_trip"):
            msg = amqp_pb2.SimpleTripOfferSearchTask(
                offer_search_id=offer_search.id,
                search=offer_search.simple_trip,
                session_token=offer_search.session_token,
                reseller_id=offer_search.reseller_id,
            )
        else:
            msg = amqp_pb2.TripOfferSearchTask(
                offer_search_id=offer_search.id,
                search=offer_search.trip,
                session_token=offer_search.session_token,
                reseller_id=offer_search.reseller_id,
            )

        if isinstance(self._producer, trackable.TrackableProducer):
            await self._producer.publish(
                msg=msg,
                routing_key=self._routing_key,
                expiration=self._ttl,
                trackable_id=offer_search.id,
            )
        else:
            await self._producer.publish(
                msg=msg,
                routing_key=self._routing_key,
            )


class PriceQuoteProducer:
    def __init__(
        self,
        producer: protocol.Producer,
        routing_key: str,
        offers_options_repository: OfferOptionsRepository,
    ):
        self._producer = producer
        self._routing_key = routing_key
        self._offers_options_repository = offers_options_repository

    async def publish(
        self,
        price_quote_container: models_pb2.PriceQuoteContainer,
        reseller_id: str,
    ) -> None:
        options = await self._offers_options_repository.find(
            list(price_quote_container.option_ids),
            "",
        )
        original_option_ids = [
            offer.initial_offer_id or offer.id async for offer in options
        ]

        await asyncio.gather(
            *[
                self._producer.publish(
                    msg=amqp_pb2.TripPriceQuoteTask(
                        price_quote_container_id=price_quote_container.id,
                        option_id=option_id,
                        session_token=price_quote_container.session_token,
                        reseller_id=reseller_id,
                    ),
                    routing_key=self._routing_key,
                )
                for option_id in original_option_ids
            ],
        )
