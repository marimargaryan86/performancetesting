from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import (
    cache,
    conftest,
    pricing,
    transformer,
)
from snowfall.stdlib import money


async def test_search_result_data(  # noqa: WPS218, WPS210
    pricing_adapter: pricing.Adapter,
    offer_transformer: transformer.OfferTransformer,
    magic_mocker: conftest.MagicMocker,
) -> None:
    with magic_mocker.with_fixture_path("branded_search"):
        price_result = await pricing_adapter.get_price_quote(
            session_token="FOOBAR",
            offer_details=cache.OfferDetails(
                search_id="87380906a4cd4f5b812ac9328a82e54f",
                itinerary_id="3777dc8240b545b28b66f2c14a5f952f",
            ),
        )

    price_quote = await offer_transformer.to_price_quote(price_result, "foo")

    price = money.from_protobuf(price_quote.price)
    assert str(price) == "69.54"
    assert price.currency.code == "EUR"

    base_fare = price_quote.price_breakdown[0]
    base_fare_price = money.from_protobuf(base_fare.price)
    assert str(base_fare_price) == "27.00"
    assert base_fare_price.currency.code == "EUR"
    assert (
        base_fare.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    tax = price_quote.price_breakdown[1]
    tax_price = money.from_protobuf(tax.price)
    assert str(tax_price) == "42.54"
    assert tax_price.currency.code == "EUR"
    assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX
