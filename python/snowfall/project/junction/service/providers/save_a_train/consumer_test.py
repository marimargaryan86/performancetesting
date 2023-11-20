from unittest import mock

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import consumer
from snowfall.stdlib.transport.amqp import types


async def test_price_quote_consumer(
    price_quote_consumer: consumer.PriceQuoteConsumer,
    message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
) -> None:
    price_quote_consumer._producer.publish = (  # type: ignore[method-assign] # noqa: SLF001
        mock.AsyncMock()
    )
    await price_quote_consumer._process_message(message)  # noqa: SLF001
    price_quote_consumer._producer.publish.assert_awaited_once()  # noqa: SLF001
