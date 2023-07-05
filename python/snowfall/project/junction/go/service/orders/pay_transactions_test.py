from types import MappingProxyType
from unittest.mock import create_autospec

import httpx
import pytest

from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreationError,
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.v1.models_pb2 import (
    Booking,
    TripBooking,
    TripOption,
)
from snowfall.stdlib import string
from snowfall.vendor.junction.pay.client import Client as PayClient

EXTERNAL_REFERENCE = string.uuid()
INVOICE_REFERENCE = "a-provider-reference"

CREATE_TRANSACTION_RESPONSE = MappingProxyType(
    {
        "data": {
            "id": "a-transaction-id",
            "type": "transactions",
            "attributes": {
                "externalReference": EXTERNAL_REFERENCE,
                "invoiceReference": EXTERNAL_REFERENCE,
                "createdAt": "2023-04-05T14:52:25+00:00",
                "amounts": {
                    "beneficiary": {
                        "currency": "USD",
                        "amount": 1000,
                    },
                    "quotation": {
                        "currency": "SEK",
                        "amount": 10400,
                    },
                    "baseConverted": {
                        "currency": "SEK",
                        "amount": 10400,
                    },
                    "salesMargin": {
                        "currency": "SEK",
                        "amount": 0,
                    },
                    "fxMargin": {
                        "currency": "SEK",
                        "amount": 0,
                    },
                    "fxProviderMargin": {
                        "currency": "SEK",
                        "amount": 0,
                    },
                },
                "rates": {
                    "fxQuote": 10.4,
                    "fxBuffer": 0,
                    "salesMarkup": 0,
                    "fxMarkup": 0,
                },
            },
            "relationships": {
                "conversion": {
                    "data": {
                        "id": "c150562f-70ce-4540-bf4e-6b3b3f7d0b04",
                        "type": "conversions",
                    },
                },
                "payer": {
                    "data": {
                        "id": "25a2ea74-0a5d-4991-9ce0-4996be2bcceb",
                        "type": "companies",
                    },
                },
                "beneficiary": {
                    "data": {
                        "id": "ed48aa95-c449-4100-8ba8-722e882e5dde",
                        "type": "companies",
                    },
                },
            },
        },
    },
)


async def test_that_transaction_created_and_id_set_in_booking() -> None:
    mock_pay_client = create_autospec(PayClient, spec_set=True, instance=True)
    mock_pay_client.create_transactions.return_value = CREATE_TRANSACTION_RESPONSE
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        pay_client=mock_pay_client,
    )
    booking = Booking(
        id=EXTERNAL_REFERENCE,
        order_id="an-id",
        trip_option=TripOption(pay_quote_id="a-pay-quotation-id"),
        status=Booking.Status.STATUS_PENDING,
        provider_name="a-provider",
        total_price=None,
        trip_result=TripBooking(provider_booking_reference=INVOICE_REFERENCE),
        raw_data="raw data",
        created_at=None,
        updated_at=None,
    )
    updated_booking = await pay_transactions.create_transaction_and_set_id(
        booking=booking,
    )

    assert updated_booking.transaction_id == "a-transaction-id"

    mock_pay_client.create_transactions.assert_called_once_with(
        external_reference=EXTERNAL_REFERENCE,
        invoice_reference=INVOICE_REFERENCE,
        quotation_id="a-pay-quotation-id",
    )


async def test_that_exception_raised_if_error_creating_transaction_with_client() -> (
    None
):
    mock_pay_client = create_autospec(PayClient, spec_set=True, instance=True)
    expected_error = httpx.HTTPError("An Error")
    mock_pay_client.create_transactions.side_effect = expected_error
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        pay_client=mock_pay_client,
    )
    booking = Booking(
        id=EXTERNAL_REFERENCE,
        order_id="an-id",
        trip_option=TripOption(pay_quote_id="pay-quote-id"),
        status=Booking.Status.STATUS_PENDING,
        provider_name="a-provider",
        total_price=None,
        trip_result=None,
        raw_data="raw data",
        created_at=None,
        updated_at=None,
    )
    with pytest.raises(PayTransactionCreationError) as ex:
        await pay_transactions.create_transaction_and_set_id(
            booking=booking,
        )

    assert ex.value.__cause__ == expected_error  # noqa: WPS441
