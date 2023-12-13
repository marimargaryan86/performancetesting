import uuid
from collections.abc import Sequence
from unittest import mock

import pytest

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.pay_quotes import (
    PayCreateQuoteError,
    PayQuotes,
    SkippedConversionError,
)
from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.go.service.offers.v1.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import companies, quotations
from snowfall.stdlib import money, string
from snowfall.stdlib.v1 import money_pb2


@pytest.fixture()
def pay_quotes(
    quotations_client: quotations.Client,
    companies_client: companies.Client,
    offer_options_repository: offers.OfferOptionsRepository,
) -> PayQuotes:
    return PayQuotes(
        quotations_client=quotations_client,
        companies_client=companies_client,
        offer_options_repository=offer_options_repository,
    )


async def test_that_pay_quotes_invoked_and_response_returned(
    pay_quotes: PayQuotes,
) -> None:
    quote = await pay_quotes._create_quote(  # noqa: SLF001
        amount=1000,
        session_token="session-token",
        payer_company=pay_fixtures.get_companies()[0],
        beneficiary_company=pay_fixtures.get_companies()[1],
        from_currency="EUR",
        to_currency="SEK",
        tax=700,
    )

    assert quote.id


async def test_create_quote_failed_throws_create_quote_error(
    companies_client: companies.Client,
    offer_options_repository: offers.OfferOptionsRepository,
) -> None:
    quotations_client = mock.create_autospec(quotations.Client)
    quotations_client.create = mock.AsyncMock(side_effect=errors.NotFoundError)
    pay_quotes = PayQuotes(
        quotations_client=quotations_client,
        companies_client=companies_client,
        offer_options_repository=offer_options_repository,
    )

    with pytest.raises(PayCreateQuoteError):
        await pay_quotes._create_quote(  # noqa: SLF001
            amount=1000,
            session_token="session-token",
            payer_company=pay_fixtures.get_companies()[0],
            beneficiary_company=pay_fixtures.get_companies()[1],
            from_currency="EUR",
            to_currency="SEK",
            tax=700,
        )


async def test_get_company_failed_throws_create_quote_error(
    quotations_client: quotations.Client,
    offer_options_repository: offers.OfferOptionsRepository,
) -> None:
    companies_client = mock.create_autospec(companies.Client)
    companies_client.get = mock.AsyncMock(side_effect=errors.NotFoundError)
    pay_quotes = PayQuotes(
        quotations_client=quotations_client,
        companies_client=companies_client,
        offer_options_repository=offer_options_repository,
    )

    with pytest.raises(PayCreateQuoteError):
        await pay_quotes._get_company(  # noqa: SLF001
            company_id=pay_fixtures.NOT_FOUND,
        )


async def test_that_all_amounts_in_trip_offer_search_result_replaced_with_conversions(  # noqa: WPS218
    pay_quotes: PayQuotes,
) -> None:
    search_result = TripOfferSearchResult(
        offer_search_id="an-id",
        offer=models_pb2.OfferGroup(
            id="faa416e4-c7ef-11ed-afa1-0242ac120002",
            offers=[
                models_pb2.Offer(
                    id="009fd15a-c7f0-11ed-afa1-0242ac120002",
                    price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
                    price_breakdown=[
                        models_pb2.PriceBreakdown(
                            price=money_pb2.Money(
                                currency_code="EUR",
                                units=500,
                                nanos=0,
                            ),
                            breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                ),
                models_pb2.Offer(
                    id="009fd15a-c7f0-11ed-afa1-0242ac120002",
                    price=money_pb2.Money(currency_code="EUR", units=100, nanos=0),
                    price_breakdown=[
                        models_pb2.PriceBreakdown(
                            price=money_pb2.Money(
                                currency_code="EUR",
                                units=100,
                                nanos=0,
                            ),
                            breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                ),
            ],
        ),
        provider_company_id=pay_fixtures.COMPANIES[1],
    )

    modified_result = await pay_quotes.get_offer_search_quotes(
        search_result,
        "session-token",
        pay_fixtures.COMPANIES[0],
        "SEK",
    )

    for idx, offer in enumerate(modified_result.offer.offers):
        search_result_offer = search_result.offer
        assert offer.price.units == search_result_offer.offers[idx].price.units
        assert offer.price.currency_code == "SEK"
        assert offer.id == string.to_uuid(
            "session-token",
            uuid.UUID("009fd15a-c7f0-11ed-afa1-0242ac120002"),
        )
        assert offer.initial_offer_id == "009fd15a-c7f0-11ed-afa1-0242ac120002"
        _assert_price_breakdown(
            offer.price_breakdown,
            offer.price,
            expected_num_breakdowns=3,
        )

    assert modified_result.offer.id == string.to_uuid(
        "session-token",
        uuid.UUID("faa416e4-c7ef-11ed-afa1-0242ac120002"),
    )


async def test_that_price_in_trip_price_quote_result_replaced_with_conversion(
    pay_quotes: PayQuotes,
    trip_offer_repository: offers.TripOfferRepository,
) -> None:
    price_quote_result = TripPriceQuoteResult(
        price_quote_container_id="an-id",
        option_id="an-id",
        price_quote=models_pb2.PriceQuote(
            id="009fd15a-c7f0-11ed-afa1-0242ac120002",
            option_id="487b5a88-a77c-4798-bedd-ec414a1f0e88",
            expires_at=None,
            price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
            price_breakdown=[
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            ],
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id=pay_fixtures.COMPANIES[1],
    )
    expected_uuid = string.to_uuid(
        "session-token",
        uuid.UUID("487b5a88-a77c-4798-bedd-ec414a1f0e88"),
    )
    await trip_offer_repository.insert(
        models_pb2.OfferGroup(
            offers=[
                models_pb2.Offer(
                    id=expected_uuid,
                    price=money_pb2.Money(
                        currency_code="SEK",
                    ),
                ),
            ],
        ),
    )

    modified_result = await pay_quotes.get_price_quote_quotes(
        "session-token",
        price_quote_result,
        pay_fixtures.COMPANIES[0],
    )

    assert (
        modified_result.price_quote.price.units
        == price_quote_result.price_quote.price.units
    )
    assert modified_result.price_quote.price.currency_code == "SEK"
    assert modified_result.price_quote.option_id == expected_uuid
    _assert_price_breakdown(
        modified_result.price_quote.price_breakdown,
        modified_result.price_quote.price,
        expected_num_breakdowns=4,
    )


async def test_price_breakdown_when_no_tax_or_markups_returned_by_pay(
    companies_client: companies.Client,
    offer_options_repository: offers.OfferOptionsRepository,
    trip_offer_repository: offers.TripOfferRepository,
) -> None:
    zero_value_money = money.Money(0, money.Currency("SEK")).protobuf()
    price = money.Money(500, money.Currency("SEK")).protobuf()
    quotation = pay_fixtures.get_quotations()[0]
    quotation.amounts.base_converted.CopyFrom(price)
    quotation.amounts.total_amount.CopyFrom(price)
    quotation.amounts.tax_converted.CopyFrom(zero_value_money)
    quotation.amounts.service_markup.CopyFrom(zero_value_money)
    quotation.amounts.fee_amount.CopyFrom(zero_value_money)

    quotations_client = mock.create_autospec(quotations.Client)
    quotations_client.create = mock.AsyncMock(return_value=quotation)
    pay_quotes = PayQuotes(
        quotations_client=quotations_client,
        companies_client=companies_client,
        offer_options_repository=offer_options_repository,
    )

    price_quote_result = TripPriceQuoteResult(
        price_quote_container_id="an-id",
        option_id="an-id",
        price_quote=models_pb2.PriceQuote(
            id="009fd15a-c7f0-11ed-afa1-0242ac120002",
            option_id="487b5a88-a77c-4798-bedd-ec414a1f0e88",
            expires_at=None,
            price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
            price_breakdown=[
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id=pay_fixtures.COMPANIES[1],
    )
    await trip_offer_repository.insert(
        models_pb2.OfferGroup(
            offers=[
                models_pb2.Offer(
                    id=string.to_uuid(
                        "session-token",
                        uuid.UUID("487b5a88-a77c-4798-bedd-ec414a1f0e88"),
                    ),
                    price=money_pb2.Money(
                        currency_code="SEK",
                    ),
                ),
            ],
        ),
    )

    modified_result = await pay_quotes.get_price_quote_quotes(
        "session-token",
        price_quote_result,
        pay_fixtures.COMPANIES[0],
    )

    _assert_price_breakdown(
        modified_result.price_quote.price_breakdown,
        modified_result.price_quote.price,
        expected_num_breakdowns=1,
    )


async def test_get_price_quote_quotes_no_offer_found_throws_skipped_conversion_error(
    pay_quotes: PayQuotes,
) -> None:
    price_quote_result = TripPriceQuoteResult(
        price_quote_container_id="an-id",
        option_id="an-id",
        price_quote=models_pb2.PriceQuote(
            id="009fd15a-c7f0-11ed-afa1-0242ac120002",
            option_id="487b5a88-a77c-4798-bedd-ec414a1f0e88",
            expires_at=None,
            price=money_pb2.Money(currency_code="EUR", units=500, nanos=0),
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id=pay_fixtures.COMPANIES[1],
    )

    with pytest.raises(SkippedConversionError):
        await pay_quotes.get_price_quote_quotes(
            "session-token",
            price_quote_result,
            pay_fixtures.COMPANIES[0],
        )


def _assert_price_breakdown(  # noqa: WPS218
    price_breakdown: Sequence[models_pb2.PriceBreakdown],
    expected_price: money_pb2.Money,
    expected_num_breakdowns: int,
) -> None:
    assert len(price_breakdown) == expected_num_breakdowns
    for breakdown in price_breakdown:
        match breakdown.breakdown_type:
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE:
                assert breakdown.price.units == expected_price.units
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX:
                assert breakdown.price.units == expected_price.units
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_SERVICE_MARK_UP:
                assert breakdown.price.units == expected_price.units
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_RESELLER_MARK_UP:
                assert breakdown.price.units == expected_price.units
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_COMPANY_MARK_UP:
                assert breakdown.price.units == expected_price.units
                assert breakdown.price.currency_code == "SEK"
