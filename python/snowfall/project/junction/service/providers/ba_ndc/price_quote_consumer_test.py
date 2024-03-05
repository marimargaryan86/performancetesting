from __future__ import annotations

from unittest import mock

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.ba_ndc import pricing
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.ba_ndc.models import (
    response_priced_offer_schemas,
)


async def test_price_quote_consumer(
    price_quote_consumer: pricing.PriceQuoteConsumer,
    message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    mock_get_offer: response_priced_offer_schemas.PricedOfferResponse,
) -> None:
    producer = price_quote_consumer._producer  # noqa: SLF001
    producer.publish = mock.AsyncMock()  # type: ignore[method-assign]

    await price_quote_consumer._process_message(message)  # noqa: SLF001

    producer.publish.assert_awaited_once()
