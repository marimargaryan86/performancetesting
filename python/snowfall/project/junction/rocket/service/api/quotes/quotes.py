from snowfall.project.junction.rocket.service.api.flights import repositories
from snowfall.project.junction.rocket.service.api.v1alpha import pricing_pb2
from snowfall.stdlib import string
from snowfall.stdlib.transport.amqp import producer


class QuoteTaskProducer:
    def __init__(
        self,
        producer_obj: producer.Producer,
        routing_key: str,
    ):
        self._producer_obj = producer_obj
        self._routing_key = routing_key

    async def publish(self, quote: pricing_pb2.Quote) -> None:
        await self._producer_obj.publish(
            msg=pricing_pb2.CreateQuoteTask(
                quote=quote,
            ),
            routing_key=self._routing_key,
        )


class FlightQuoteManager:
    def __init__(
        self,
        quotes_repository: repositories.QuoteRepository,
        task_producer: QuoteTaskProducer,
    ):
        self._quotes_repository = quotes_repository
        self._task_producer = task_producer

    async def create(
        self,
        offer_id: str,
        reseller_id: str,
        reseller_company_id: str,
        reseller_currency: str,
    ) -> pricing_pb2.Quote:
        quote = await self._quotes_repository.insert(
            pricing_pb2.Quote(
                id=string.uuid(),
                reseller_id=reseller_id,
                reseller_company_id=reseller_company_id,
                reseller_currency=reseller_currency,
                offer_id=offer_id,
                status=pricing_pb2.Quote.STATUS_PENDING,
            ),
        )

        await self._task_producer.publish(quote)

        return quote
