from __future__ import annotations

import uuid

from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ba_ndc import cache, conftest
from snowfall.project.junction.service.providers.ba_ndc.pricing_transformer import (
    PriceQuoteTransformer,
)
from snowfall.stdlib import money
from snowfall.vendor.ba_ndc.models.response_offer_search_schemas import (
    OfferSearchResponse,
)


class TestPricingTransformer(object):
    async def test_offer_to_price_quote_price(  # noqa: WPS218
        self,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        json_res = await conftest.load_file_fixture("get_offers_response.json")
        offer_search_response = OfferSearchResponse.parse_obj(json_res)

        offer = offer_search_response.offers[0]
        price_quote_details = cache.PriceQuoteDetails(
            offer_id=offer.identifier,
            price=cache.Price(
                amount=offer.price.total_amount,
                currency=offer.price.currency,
            ),
            price_breakdown=cache.PriceBreakdown(
                currency=offer.price.currency,
                tax_amount=offer.price.tax_amount,
                base_amount=offer.price.base_amount,
            ),
            passengers=[],
            expires_at=offer_search_response.expires_at,
            penalties=[],
            is_international_flight=True,
            has_flight_with_usa_destination=True,
        )

        transformer = PriceQuoteTransformer()
        price_quote = transformer.to_price_quote(
            price_quote_details_id=str(uuid.uuid4()),
            price_quote_details=price_quote_details,
            option_id=str(uuid.uuid4()),
        )

        price = money.from_protobuf(price_quote.price)
        assert str(price) == "49.46"
        assert price.currency.code == "EUR"

        base_fare = price_quote.price_breakdown[0]  # noqa: WPS432
        base_fare_price = money.from_protobuf(base_fare.price)
        assert str(base_fare_price) == "14.00"
        assert base_fare_price.currency.code == "EUR"
        assert (
            base_fare.breakdown_type
            == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
        )

        tax = price_quote.price_breakdown[1]
        tax_price = money.from_protobuf(tax.price)
        assert str(tax_price) == "35.46"
        assert tax_price.currency.code == "EUR"
        assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX
