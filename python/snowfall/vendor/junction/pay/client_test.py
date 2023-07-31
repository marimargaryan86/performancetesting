import uuid
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_httpx

from snowfall.vendor.junction.pay.client import Client as PayClient

_EXTERNAL_REFERENCE = "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"
_PAYER_ID = str(uuid.uuid4())
_BENEFICIARY_ID = str(uuid.uuid4())


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
async def pay_client(
    httpx_client: httpx.AsyncClient,
) -> PayClient:
    return PayClient(
        base_url="https://api.pay.junction.dev",
        client=httpx_client,
    )


class TestPayClient(object):
    async def test_create_quote(
        self,
        pay_client: PayClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        create_quote_response = {
            "data": {
                "id": str(uuid.uuid4()),
                "type": "quotes",
                "attributes": {
                    "amount": 1000,
                    "tax": 337,
                    "totalMarkups": 23,
                    "totalAmount": 1700,
                    "resellerMarkup": 100,
                    "leadCompanyMarkup": 100,
                    "externalReference": _EXTERNAL_REFERENCE,
                },
                "relationships": {
                    "fromCurrency": {"data": {"id": "EUR", "type": "currencies"}},
                    "toCurrency": {"data": {"id": "SEK", "type": "currencies"}},
                    "payer": {
                        "data": {
                            "id": _PAYER_ID,
                            "type": "companies",
                        },
                    },
                    "beneficiary": {
                        "data": {
                            "id": _BENEFICIARY_ID,
                            "type": "companies",
                        },
                    },
                },
            },
        }

        httpx_mock.add_response(
            url="https://api.pay.junction.dev/quotes",
            status_code=200,
            json=create_quote_response,
        )

        response = await pay_client.create_quote(
            amount=123,
            external_reference=_EXTERNAL_REFERENCE,
            payer_id=_PAYER_ID,
            beneficiary_id=_BENEFICIARY_ID,
            from_currency="EUR",
            to_currency="SEK",
            tax=100,
        )

        assert response == create_quote_response

    async def test_create_quote_no_tax(
        self,
        pay_client: PayClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        no_tax_response = {
            "data": {
                "id": str(uuid.uuid4()),
                "type": "quotes",
                "attributes": {
                    "amount": 1000,
                    "tax": 0,
                    "totalMarkups": 23,
                    "totalAmount": 1700,
                    "resellerMarkup": 100,
                    "leadCompanyMarkup": 100,
                    "externalReference": _EXTERNAL_REFERENCE,
                },
                "relationships": {
                    "fromCurrency": {"data": {"id": "EUR", "type": "currencies"}},
                    "toCurrency": {"data": {"id": "SEK", "type": "currencies"}},
                    "payer": {
                        "data": {
                            "id": _PAYER_ID,
                            "type": "companies",
                        },
                    },
                    "beneficiary": {
                        "data": {
                            "id": _BENEFICIARY_ID,
                            "type": "companies",
                        },
                    },
                },
            },
        }

        httpx_mock.add_response(
            url="https://api.pay.junction.dev/quotes",
            status_code=200,
            json=no_tax_response,
        )

        response = await pay_client.create_quote(
            amount=123,
            external_reference=_EXTERNAL_REFERENCE,
            payer_id=_PAYER_ID,
            beneficiary_id=_BENEFICIARY_ID,
            from_currency="EUR",
            to_currency="SEK",
        )

        assert response == no_tax_response

    async def test_create_transactions(
        self,
        pay_client: PayClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        create_transaction_response = {
            "data": {
                "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                "type": "transactions",
                "attributes": {
                    "externalReference": _EXTERNAL_REFERENCE,
                    "invoiceReference": "k1234567890123",
                    "createdAt": "2023-01-20T17:04:14+00:00",
                    "amounts": {
                        "beneficiary": {"currency": "EUR", "amount": 1337},
                        "quotation": {"currency": "EUR", "amount": 1337},
                        "baseConverted": {"currency": "EUR", "amount": 1337},
                        "salesMargin": {"currency": "EUR", "amount": 1337},
                        "fxMargin": {"currency": "EUR", "amount": 1337},
                        "processingMargin": {"currency": "EUR", "amount": 1337},
                    },
                    "rates": {
                        "fxQuote": 1.02,
                        "fxBuffer": 1.02,
                        "salesMarkup": 1.02,
                        "fxMarkup": 1.02,
                        "processingMarkup": 1.02,
                    },
                },
                "relationships": {
                    "conversion": {
                        "data": {
                            "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                            "type": "conversions",
                        },
                    },
                    "payer": {
                        "data": {
                            "id": "04f83af5-10bb-4a0f-1881-03e1e690f0f5",
                            "type": "companies",
                        },
                    },
                    "beneficiary": {
                        "data": {
                            "id": "04f83af5-10bb-4a0f-1881-03e1e690f0f5",
                            "type": "companies",
                        },
                    },
                },
                "links": {
                    "self": "https://example.com/resource/04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                },
            },
        }

        httpx_mock.add_response(
            url="https://api.pay.junction.dev/transactions",
            status_code=201,
            json=create_transaction_response,
        )

        response = await pay_client.create_transactions(
            external_reference=_EXTERNAL_REFERENCE,
            invoice_reference="k1234567890123",
            quotation_id="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
        )

        assert response == create_transaction_response

    async def test_list_all_currencies(
        self,
        pay_client: PayClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        list_all_currencies_reponse = {
            "data": [
                {
                    "id": "USD",
                    "type": "currencies",
                    "attributes": {"name": "US Dollar", "minorUnits": 2},
                    "links": {
                        "self": "https://example.com/resource/04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                    },
                },
            ],
        }

        httpx_mock.add_response(
            url="https://api.pay.junction.dev/currencies",
            status_code=200,
            json=list_all_currencies_reponse,
        )

        response = await pay_client.list_all_currencies()

        assert response == list_all_currencies_reponse
