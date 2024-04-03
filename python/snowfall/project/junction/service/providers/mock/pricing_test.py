import datetime

import more_itertools
import pytest

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.mock import cache, pricing
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf

_UNKNOWN_OFFER = "bf624a85-205a-4717-b4e7-a83f6ec8ecb9"


class TestQuoter:
    async def test_unknown_option_id_raises_error(
        self,
        quoter: pricing.Quoter,
    ) -> None:
        with pytest.raises(cache.OptionNotFoundError):
            await quoter.generate_quote(_UNKNOWN_OFFER)

    async def test_known_option_id_returns_quote(
        self,
        option_cache: cache.OptionCache,
        quoter: pricing.Quoter,
    ) -> None:
        option_id = await option_cache.store(
            cache.MockDetails(
                amount=1,
                currency="USD",
            ),
        )
        assert await quoter.generate_quote(option_id) is not None


class TestPriceQuoteModel:
    def test_has_id(self, price_quote: offers_pb2.PriceQuote) -> None:
        assert price_quote.id

    def test_has_expiry(self, price_quote: offers_pb2.PriceQuote) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        assert protobuf.protobuf_to_datetime(price_quote.expires_at) > now

    def test_has_option_id(
        self,
        price_quote: offers_pb2.PriceQuote,
        option_id: str,
    ) -> None:
        assert price_quote.option_id == option_id

    def test_has_price(
        self,
        price_quote: offers_pb2.PriceQuote,
        price: money.Money,
    ) -> None:
        assert (
            price_quote.price.SerializeToString()
            == price.protobuf().SerializeToString()
        )

    def test_has_fare_rules(self, price_quote: offers_pb2.PriceQuote) -> None:
        assert price_quote.rules

        first_rule = more_itertools.first(price_quote.rules)

        assert first_rule.title
        assert first_rule.body
