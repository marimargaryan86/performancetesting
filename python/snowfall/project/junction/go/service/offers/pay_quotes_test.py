import uuid
from types import MappingProxyType
from unittest import mock

import pytest

from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.pay_quotes import PayQuotes
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

    quote = await pay_quotes._get_quote(  # noqa: WPS437
        amount=1000,
        session_token="session-token",
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
    )

    assert quote == expected_resp
    mock_pay_client.create_quote.assert_called_once_with(
        amount=1000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="beneficiary-id",
        from_currency="EUR",
        to_currency="SEK",
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
                ),
                models_pb2.Offer(
                    id="009fd15a-c7f0-11ed-afa1-0242ac120002",
                    price=money_pb2.Money(currency_code="EUR", units=100, nanos=0),
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
        assert offer.price.units == 15
        assert offer.price.currency_code == "SEK"
        assert offer.id == string.to_uuid(
            "session-token",
            uuid.UUID("009fd15a-c7f0-11ed-afa1-0242ac120002"),
        )
        assert offer.initial_offer_id == "009fd15a-c7f0-11ed-afa1-0242ac120002"

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
    )
    mock_pay_client.create_quote.assert_any_call(
        amount=10000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
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

    assert modified_result.price_quote.price.units == 15
    assert modified_result.price_quote.price.currency_code == "SEK"
    assert modified_result.price_quote.pay_quote_id == "a-quotation-id"
    assert modified_result.price_quote.option_id == expected_uuid

    mock_pay_client.create_quote.assert_called_once_with(
        amount=50000,
        external_reference="session-token",
        payer_id="payer-id",
        beneficiary_id="provider-id-1",
        from_currency="EUR",
        to_currency="SEK",
    )
