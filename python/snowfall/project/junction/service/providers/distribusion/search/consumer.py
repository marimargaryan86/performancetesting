from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.distribusion.search.adapter import (
    DistribusionSearchAdapter,
)
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib.transport.amqp import consumer, producer, types


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.SearchCriteriaTask],
        producer_obj: producer.Producer,
        adapter: DistribusionSearchAdapter,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = adapter

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.SearchCriteriaTask],
    ) -> None:
        async for offer_result in self._adapter.gather_search_results(message.body):
            await self._producer.publish(
                offers_amqp_pb2.TripOfferSearchResult(
                    offer_search_id=message.body.offer_search_id,
                    offer=offer_result,
                ),
                routing_key="offers.result.trip",
            )
