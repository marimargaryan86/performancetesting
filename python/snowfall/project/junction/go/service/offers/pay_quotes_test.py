import uuid
from types import MappingProxyType
from unittest.mock import create_autospec

from snowfall.project.junction.go.service.offers.pay_quotes import (
    PayQuoteResponse,
    PayQuotes,
)
from snowfall.project.junction.go.service.offers.pay_quotes_models import (
    PayQuoteAttributes,
    PayQuoteCompany,
    PayQuoteCompanyData,
    PayQuoteCurrency,
    PayQuoteCurrencyData,
    PayQuoteData,
    PayQuoteRelationships,
)
from snowfall.project.junction.go.service.offers.v1alpha.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.project.junction.go.service.offers.v1alpha.models_pb2 import (
    Offer,
    OfferGroup,
    PriceQuote,
)
from snowfall.stdlib import string
from snowfall.stdlib.v1alpha.money_pb2 import Money
from snowfall.vendor.junction.pay.client import Client as PayClient

_QUOTE_MOCK_RESPONSE = MappingProxyType(
    {
        "id": "a-quotation-id",
        "data": {
            "type": "quotes",
            "attributes": {
                "amount": 1500,
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


async def test_that_pay_quotes_invoked_and_response_returned() -> None:
    mock_pay_client = create_autospec(PayClient, spec_set=True, instance=True)
    pay_quotes = PayQuotes(pay_client=mock_pay_client)
    mock_resp = _QUOTE_MOCK_RESPONSE
    expected_resp = PayQuoteResponse(
        id="a-quotation-id",
        data=PayQuoteData(
            type="quotes",
            attributes=PayQuoteAttributes(
                amount=1500,
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

    mock_pay_client.create_quote.return_value = mock_resp

    quote = await pay_quotes._get_quote(  # noqa:WPS437
        amount=1000,
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
    )

    assert quote == expected_resp
    mock_pay_client.create_quote.assert_called_once_with(
        amount=1000,
        external_reference="",
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
    )


async def test_that_all_amounts_in_trip_offer_search_result_replaced_with_conversions() -> (  # noqa:WPS210,B950
    None
):
    mock_pay_client = create_autospec(PayClient, spec_set=True, instance=True)
    pay_quotes = PayQuotes(pay_client=mock_pay_client)
    mock_resp = _QUOTE_MOCK_RESPONSE

    mock_pay_client.create_quote.return_value = mock_resp

    search_result = TripOfferSearchResult(
        offer_search_id="an-id",
        offer=OfferGroup(
            id="faa416e4-c7ef-11ed-afa1-0242ac120002",
            offers=[
                Offer(
                    id="009fd15a-c7f0-11ed-afa1-0242ac120002",
                    price=Money(currency_code="EUR", units=500, nanos=0),
                ),
                Offer(
                    id="009fd15a-c7f0-11ed-afa1-0242ac120002",
                    price=Money(currency_code="EUR", units=100, nanos=0),
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
        assert offer.price.units == 1500
        assert offer.price.currency_code == "SEK"
        assert offer.id == string.to_uuid(
            "session-token",
            uuid.UUID("009fd15a-c7f0-11ed-afa1-0242ac120002"),
        )

    assert modified_result.offer.id == string.to_uuid(
        "session-token",
        uuid.UUID("faa416e4-c7ef-11ed-afa1-0242ac120002"),
    )

    mock_pay_client.create_quote.assert_any_call(
        amount=50000,
        external_reference="",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
    )
    mock_pay_client.create_quote.assert_any_call(
        amount=10000,
        external_reference="",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
    )
    assert mock_pay_client.create_quote.call_count == 2


async def test_that_price_in_trip_price_quote_result_replaced_with_conversion() -> None:
    mock_pay_client = create_autospec(PayClient, spec_set=True, instance=True)
    pay_quotes = PayQuotes(pay_client=mock_pay_client)
    mock_resp = _QUOTE_MOCK_RESPONSE

    mock_pay_client.create_quote.return_value = mock_resp

    price_quote_result = TripPriceQuoteResult(
        price_quote_container_id="an-id",
        option_id="an-id",
        price_quote=PriceQuote(
            id="009fd15a-c7f0-11ed-afa1-0242ac120002",
            option_id="an-id",
            expires_at=None,
            price=Money(currency_code="EUR", units=500, nanos=0),
            required_documents=None,
            penalties=None,
            rules=None,
        ),
        provider_company_id="provider-id-1",
    )

    modified_result = await pay_quotes.get_price_quote_quotes(
        price_quote_result,
        "session-token",
        "payer-id",
        "SEK",
    )

    assert modified_result.price_quote.price.units == 1500
    assert modified_result.price_quote.price.currency_code == "SEK"
    assert modified_result.price_quote.id == string.to_uuid(
        "session-token",
        uuid.UUID("009fd15a-c7f0-11ed-afa1-0242ac120002"),
    )
    assert modified_result.price_quote.pay_quote_id == "a-quotation-id"

    mock_pay_client.create_quote.assert_called_once_with(
        amount=50000,
        external_reference="",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
    )
