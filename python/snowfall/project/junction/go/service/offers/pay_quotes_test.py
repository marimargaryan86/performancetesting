import uuid
from collections.abc import Sequence
from types import MappingProxyType
from typing import Any
from unittest import mock

import pytest

from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.pay_quotes import (
    PayQuotes,
    SkippedConversionError,
)
from snowfall.project.junction.go.service.offers.pay_quotes_models import (
    PayQuoteAttributes,
    PayQuoteCompany,
    PayQuoteCompanyData,
    PayQuoteCurrency,
    PayQuoteCurrencyData,
    PayQuoteRelationships,
    PayQuoteResponse,
    PayQuoteResponseData,
)
from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.go.service.offers.v1.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.stdlib import string
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.junction.pay.client import Client as PayClient

_QUOTE_MOCK_RESPONSE = MappingProxyType(
    {
        "data": {
            "id": "a-quotation-id",
            "type": "quotes",
            "attributes": {
                "amount": 1000,
                "tax": 700,
                "totalMarkups": 300,
                "totalAmount": 2000,
                "serviceMarkup": 100,
                "feeAmount": 100,
            },
            "relationships": {
                "fromCurrency": {
                    "data": {
                        "id": "EUR",
                        "type": "currencies",
                    },
                },
                "toCurrency": {
                    "data": {
                        "id": "SEK",
                        "type": "currencies",
                    },
                },
                "payer": {
                    "data": {
                        "id": "payer-id",
                        "type": "companies",
                    },
                },
                "beneficiary": {
                    "data": {
                        "id": "beneficiary-id",
                        "type": "companies",
                    },
                },
            },
        },
    },
)


@pytest.fixture()
def mock_pay_client() -> mock.Mock:
    mock_pay_client = mock.create_autospec(PayClient, spec_set=True, instance=True)
    mock_pay_client.create_quote.return_value = _QUOTE_MOCK_RESPONSE

    return mock_pay_client


@pytest.fixture()
def pay_quotes(
    mock_pay_client: mock.Mock,
    offer_options_repository: offers.OfferOptionsRepository,
) -> PayQuotes:
    return PayQuotes(
        pay_client=mock_pay_client,
        offer_options_repository=offer_options_repository,
    )


async def test_that_pay_quotes_invoked_and_response_returned(
    mock_pay_client: mock.Mock,
    pay_quotes: PayQuotes,
) -> None:
    expected_resp = PayQuoteResponse(
        data=PayQuoteResponseData(
            id="a-quotation-id",
            type="quotes",
            attributes=PayQuoteAttributes(
                amount=1000,
                tax=700,
                total_markups=300,
                total_amount=2000,
                service_markup=100,
                reseller_markup=100,
            ),
            relationships=PayQuoteRelationships(
                from_currency=PayQuoteCurrency(
                    data=PayQuoteCurrencyData(
                        id="EUR",
                    ),
                ),
                to_currency=PayQuoteCurrency(
                    data=PayQuoteCurrencyData(
                        id="SEK",
                    ),
                ),
                payer=PayQuoteCompany(
                    data=PayQuoteCompanyData(
                        id="payer-id",
                    ),
                ),
                beneficiary=PayQuoteCompany(
                    data=PayQuoteCompanyData(
                        id="beneficiary-id",
                    ),
                ),
            ),
        ),
    )

    quote = await pay_quotes._get_quote(  # noqa: SLF001
        amount=1000,
        session_token="session-token",
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
        tax=700,
    )

    assert quote == expected_resp
    mock_pay_client.create_quote.assert_called_once_with(
        amount=1000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
        tax=700,
    )


async def test_that_all_amounts_in_trip_offer_search_result_replaced_with_conversions(  # noqa: WPS218
    mock_pay_client: mock.Mock,
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
        provider_company_id="provider-id-1",
    )

    modified_result = await pay_quotes.get_offer_search_quotes(
        search_result,
        "session-token",
        "payer-id",
        "SEK",
    )

    for offer in modified_result.offer.offers:
        assert offer.price.units == 20
        assert offer.price.currency_code == "SEK"
        assert offer.id == string.to_uuid(
            "session-token",
            uuid.UUID("009fd15a-c7f0-11ed-afa1-0242ac120002"),
        )
        assert offer.initial_offer_id == "009fd15a-c7f0-11ed-afa1-0242ac120002"
        _assert_price_breakdown(offer.price_breakdown, expected_num_breakdowns=4)

    assert modified_result.offer.id == string.to_uuid(
        "session-token",
        uuid.UUID("faa416e4-c7ef-11ed-afa1-0242ac120002"),
    )

    mock_pay_client.create_quote.assert_any_call(
        amount=50000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
        tax=None,
    )
    mock_pay_client.create_quote.assert_any_call(
        amount=10000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
        tax=None,
    )
    assert mock_pay_client.create_quote.call_count == 2


async def test_that_price_in_trip_price_quote_result_replaced_with_conversion(
    mock_pay_client: mock.Mock,
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
                    price=money_pb2.Money(currency_code="EUR", units=400, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=100, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            ],
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id="provider-id-1",
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
        "payer-id",
    )

    assert modified_result.price_quote.price.units == 20
    assert modified_result.price_quote.price.currency_code == "SEK"
    assert modified_result.price_quote.pay_quote_id == "a-quotation-id"
    assert modified_result.price_quote.option_id == expected_uuid
    _assert_price_breakdown(
        modified_result.price_quote.price_breakdown,
        expected_num_breakdowns=4,
    )

    mock_pay_client.create_quote.assert_called_once_with(
        amount=40000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
        tax=10000,
    )


async def test_that_pay_called_with_tax_when_tax_provided_in_price_quote(
    mock_pay_client: mock.Mock,
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
                    price=money_pb2.Money(currency_code="EUR", units=400, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=100, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            ],
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id="provider-id-1",
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

    await pay_quotes.get_price_quote_quotes(
        "session-token",
        price_quote_result,
        "payer-id",
    )

    mock_pay_client.create_quote.assert_called_once_with(
        amount=40000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
        tax=10000,
    )


async def test_price_breakdown_when_no_tax_or_markups_returned_by_pay(
    mock_pay_client: mock.Mock,
    pay_quotes: PayQuotes,
    trip_offer_repository: offers.TripOfferRepository,
) -> None:
    no_tax_or_markups_response = dict[str, Any](_QUOTE_MOCK_RESPONSE)
    no_tax_or_markups_response["data"]["attributes"]["tax"] = 0
    no_tax_or_markups_response["data"]["attributes"]["serviceMarkup"] = 0
    no_tax_or_markups_response["data"]["attributes"]["feeAmount"] = 0
    mock_pay_client.create_quote.return_value = no_tax_or_markups_response

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
                    price=money_pb2.Money(currency_code="EUR", units=400, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
                models_pb2.PriceBreakdown(
                    price=money_pb2.Money(currency_code="EUR", units=100, nanos=0),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            ],
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id="provider-id-1",
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
        "payer-id",
    )

    _assert_price_breakdown(
        modified_result.price_quote.price_breakdown,
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
        provider_company_id="provider-id-1",
    )

    with pytest.raises(SkippedConversionError):
        await pay_quotes.get_price_quote_quotes(
            "session-token",
            price_quote_result,
            "payer-id",
        )


def _assert_price_breakdown(  # noqa: WPS218
    price_breakdown: Sequence[models_pb2.PriceBreakdown],
    expected_num_breakdowns: int,
) -> None:
    assert len(price_breakdown) == expected_num_breakdowns
    for breakdown in price_breakdown:
        match breakdown.breakdown_type:
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE:
                assert breakdown.price.units == 10
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX:
                assert breakdown.price.units == 7
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_SERVICE_MARK_UP:
                assert breakdown.price.units == 1
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_RESELLER_MARK_UP:
                assert breakdown.price.units == 1
                assert breakdown.price.currency_code == "SEK"
            case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_COMPANY_MARK_UP:
                assert breakdown.price.units == 1
                assert breakdown.price.currency_code == "SEK"
