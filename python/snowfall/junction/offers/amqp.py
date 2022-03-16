from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib.transport import amqp


class OfferSearchProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(self, offer_search: offers_pb2.OfferSearch) -> None:
        await self._producer.publish(
            offers_pb2.TripOfferSearchTask(
                offer_search_id=offer_search.id,
                search=offer_search.trip,
            ),
            "offers.search.trip",
        )
