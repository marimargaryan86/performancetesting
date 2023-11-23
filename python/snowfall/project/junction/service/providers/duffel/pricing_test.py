from __future__ import annotations

import uuid
from unittest import mock

from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.duffel import cache, conftest, pricing
from snowfall.project.junction.service.providers.duffel.pricing_transformer import (
    PriceQuoteTransformer,
)
from snowfall.stdlib import money
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.duffel.models.single_offer import SingleOfferResponse


class TestPricingTransformer(object):
    async def test_offer_to_price_quote_price(  # noqa: WPS218
        self,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        json_res = await conftest.load_file_fixture("single_offer.json")

        offer = SingleOfferResponse.model_validate(json_res).response_data

        transformer = PriceQuoteTransformer(
            offer_cache=cache.OfferCache(client=redis.Client(redis_client)),
        )
        price_quote = transformer.to_price_quote(
            str(uuid.uuid4()),
            offer,
            str(uuid.uuid4()),
        )

        price = money.from_protobuf(price_quote.price)
        assert str(price) == "500.16"
        assert price.currency.code == "GBP"

        base_fare = price_quote.price_breakdown[0]
        base_fare_price = money.from_protobuf(base_fare.price)
        assert str(base_fare_price) == "194.69"
        assert base_fare_price.currency.code == "GBP"
        assert (
            base_fare.breakdown_type
            == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
        )

        tax = price_quote.price_breakdown[1]
        tax_price = money.from_protobuf(tax.price)
        assert str(tax_price) == "305.47"
        assert tax_price.currency.code == "GBP"
        assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX


class TestPriceQuoteConsumer(object):
    async def test_price_quote_consumer(
        self,
        price_quote_consumer: pricing.PriceQuoteConsumer,
        message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        json_res = await conftest.load_file_fixture("single_offer.json")
        offer = SingleOfferResponse.model_validate(json_res).response_data

        price_quote_consumer._producer.publish = (  # type: ignore[method-assign] # noqa: SLF001
            mock.AsyncMock()
        )

        with mock.patch(
            "snowfall.project.junction.service.providers.duffel.pricing_adapter."
            "PricingAdapter.refresh_offer",
            return_value=offer,
        ):
            await price_quote_consumer._process_message(message)  # noqa: SLF001
            price_quote_consumer._producer.publish.assert_awaited_once()  # noqa: SLF001
