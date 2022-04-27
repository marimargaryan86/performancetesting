from snowfall.junction.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport import amqp


class OfferSearchProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(self, offer_search: models_pb2.OfferSearch) -> None:
        await self._producer.publish(
            amqp_pb2.TripOfferSearchTask(
                offer_search_id=offer_search.id,
                search=offer_search.trip,
            ),
            "offers.search.trip",
        )
