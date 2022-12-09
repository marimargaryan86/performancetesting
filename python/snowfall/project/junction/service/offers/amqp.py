import asyncio

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport.amqp import protocol


class OfferSearchProducer(object):
    def __init__(
        self,
        producer: protocol.Producer,
        routing_key: str,
    ):
        self._producer = producer
        self._routing_key = routing_key

    async def publish(
        self,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        await asyncio.gather(
            self._producer.publish(
                amqp_pb2.TripOfferSearchTask(
                    offer_search_id=offer_search.id,
                    search=offer_search.trip,
                    session_token=offer_search.session_token,
                ),
                self._routing_key,
            ),
        )


class PriceQuoteProducer(object):
    def __init__(
        self,
        producer: protocol.Producer,
        routing_key: str,
    ):
        self._producer = producer
        self._routing_key = routing_key

    async def publish(
        self,
        price_quote_container: models_pb2.PriceQuoteContainer,
    ) -> None:
        await asyncio.gather(
            self._producer.publish(
                amqp_pb2.TripPriceQuoteTask(
                    price_quote_container_id=price_quote_container.id,
                    option_id=option_id,
                    session_token=price_quote_container.session_token,
                ),
                self._routing_key,
            )
            for option_id in price_quote_container.option_ids
        )
