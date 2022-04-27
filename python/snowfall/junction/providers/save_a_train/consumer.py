from typing import cast

from snowfall.junction.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.junction.providers.save_a_train import adapter as sat_adapter
from snowfall.junction.providers.save_a_train import criteria
from snowfall.junction.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib.transport import amqp


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        generator: criteria.CriteriaGenerator,
    ):
        self._consumer = consumer
        self._producer = producer
        self._generator = generator

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(offers_amqp_pb2.TripOfferSearchTask, message.body)

        for task in self._generator.from_search_task(search):
            await self._producer.publish(task, routing_key="offers.search.trip")


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        adapter: sat_adapter.SaveATrainAdapter,
    ):
        self._consumer = consumer
        self._producer = producer
        self._adapter = adapter

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(amqp_pb2.SearchCriteriaTask, message.body)

        async for offer_result in self._adapter.gather_search_results(search):
            await self._producer.publish(offer_result, routing_key="offers.result.trip")
