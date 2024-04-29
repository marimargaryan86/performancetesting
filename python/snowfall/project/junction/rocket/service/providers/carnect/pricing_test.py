from unittest import mock

from snowfall.project.junction.rocket.service.providers.carnect.pricing import (
    QuoteResultProducer,
    QuoteTaskConsumer,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
)
from snowfall.stdlib.transport.amqp import producer, types


async def test_consume_process_message_successful(
    mock_message: types.Message[amqp_pb2.QuoteTask],
    consumer_mock: QuoteTaskConsumer,
) -> None:
    mock_producer = QuoteResultProducer(
        mock.AsyncMock(spec=producer.Producer),
        "test_routing_key",
    )
    mock_producer.publish = mock.AsyncMock()  # type: ignore[method-assign]
    consumer_mock._quote_result_producer = mock_producer  # noqa: SLF001

    await consumer_mock._process_message(mock_message)  # noqa: SLF001

    mock_producer.publish.assert_awaited_once()

    quote = mock_producer.publish.call_args[0][0].quote  # noqa: WPS219
    assert quote.id == mock_message.body.quote.id
    assert quote.pay_company_id == mock_message.body.quote.pay_company_id
    assert (
        quote.total_price.currency_code
        == mock_message.body.quote.total_price.currency_code
    )
    assert quote.total_price.units == mock_message.body.quote.total_price.units
    assert quote.offer_ids == mock_message.body.quote.offer_ids
