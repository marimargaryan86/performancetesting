from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport.amqp import producer


class OfferSearchProducer(object):
    def __init__(self, producer_obj: producer.Producer):
        self._producer = producer_obj

    async def publish(
        self,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        await self._producer.publish(
            amqp_pb2.TripOfferSearchTask(
                offer_search_id=offer_search.id,
                search=offer_search.trip,
                session_token=offer_search.session_token,
            ),
            "offers.search.trip",
        )
