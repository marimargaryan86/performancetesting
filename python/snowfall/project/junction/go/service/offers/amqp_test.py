from typing import AsyncIterator
from unittest.mock import create_autospec

from snowfall.project.junction.go.service.offers.amqp import PriceQuoteProducer
from snowfall.project.junction.go.service.offers.offers import OfferOptionsRepository
from snowfall.project.junction.go.service.offers.v1alpha.models_pb2 import (
    Offer,
    PriceQuoteContainer,
)
from snowfall.stdlib.transport.amqp.producer import Producer


class MockResultSet(object):
    def __init__(self) -> None:
        self._offers = [
            Offer(
                id="mutated-id-1",
                segment_details=None,
                price=None,
                brand_name="",
                baggage_allowances=None,
                initial_offer_id="original-id-1",
            ),
            Offer(
                id="original-id-2",
                segment_details=None,
                price=None,
                brand_name="",
                baggage_allowances=None,
            ),
        ]
        self._index = 0

    def __aiter__(self) -> AsyncIterator[Offer]:
        return self

    async def __anext__(self) -> Offer:
        if self._index >= len(self._offers):
            raise StopAsyncIteration
        self._index += 1

        return self._offers[self._index - 1]


async def test_original_id_is_always_published() -> None:  # noqa: WPS210
    mock_producer = create_autospec(Producer, spec_set=True, instance=True)
    mock_offer_options_repository = create_autospec(
        OfferOptionsRepository,
        spec_set=True,
        instance=True,
    )
    mock_offer_options_repository.find.return_value = MockResultSet()
    to_test = PriceQuoteProducer(
        producer=mock_producer,
        routing_key="a-routing-key",
        offers_options_repository=mock_offer_options_repository,
    )
    price_quote_container = PriceQuoteContainer(  # nosec
        id="price-quote-container-id",
        session_token="a-session-token",
    )
    await to_test.publish(price_quote_container)

    publish_calls = mock_producer.publish.mock_calls
    assert mock_producer.publish.call_count == 2
    option_ids = [
        publish_calls[0][2]["msg"].option_id,
        publish_calls[1][2]["msg"].option_id,
    ]
    assert all(id_ in {"original-id-1", "original-id-2"} for id_ in option_ids)
