from __future__ import annotations

import uuid

from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.duffel import cache, conftest
from snowfall.project.junction.service.providers.duffel.pricing_transformer import (
    PriceQuoteTransformer,
)
from snowfall.stdlib import money
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.duffel.models.single_offer import SingleOfferResponse


class TestPricingTransformer(object):
    async def test_offer_to_price_quote_price(  # noqa: WPS218, WPS210
        self,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        json_res = conftest.load_file_fixture("single_offer.json")
        offer = SingleOfferResponse.parse_obj(json_res).response_data

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
            == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FEE
        )

        tax = price_quote.price_breakdown[1]
        tax_price = money.from_protobuf(tax.price)
        assert str(tax_price) == "305.47"
        assert tax_price.currency.code == "GBP"
        assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX
