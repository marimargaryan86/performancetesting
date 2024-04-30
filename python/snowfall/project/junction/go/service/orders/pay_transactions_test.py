from unittest import mock

import pytest

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreationError,
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.v1.models_pb2 import (
    Booking,
    TripBooking,
    TripOption,
)
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import transactions
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout


@pytest.fixture()
def booking() -> Booking:
    return Booking(
        id=string.uuid(),
        order_id=string.uuid(),
        trip_option=TripOption(pay_quote_id=pay_fixtures.QUOTATIONS[0]),
        status=Booking.Status.STATUS_PENDING,
        provider_name="a-provider",
        total_price=None,
        trip_result=TripBooking(provider_booking_reference="a-provider-reference"),
        raw_data="raw data",
        created_at=None,
        updated_at=None,
        transaction_id="",
    )


async def test_that_transaction_is_created(
    transactions_client: transactions.Client,
    booking: Booking,
) -> None:
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_client,
    )

    transaction_id = await pay_transactions.create_transaction(
        booking=booking,
    )

    booking.transaction_id = transaction_id

    assert booking.transaction_id


async def test_that_transaction_not_created(
    transactions_client: transactions.Client,
    booking: Booking,
) -> None:
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=False,
        transactions_client=transactions_client,
    )

    transaction_id = await pay_transactions.create_transaction(
        booking=booking,
    )

    booking.transaction_id = transaction_id

    assert not booking.transaction_id


async def test_quotation_not_in_quoted_status_raises_error(
    booking: Booking,
) -> None:
    quotation = pay_fixtures.get_quotations()[0]
    quotation.status = (
        transactions_models_pb2.QuotationStatus.QUOTATION_STATUS_CONFIRMED
    )

    transactions_mock_client = mock.create_autospec(transactions.Client)
    transactions_mock_client.create = mock.AsyncMock(
        side_effect=errors.UnhandledError("Quotation not valid"),
    )

    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_mock_client,
    )

    with pytest.raises(PayTransactionCreationError):
        await pay_transactions.create_transaction(
            booking=booking,
        )


async def test_create_transaction_logs_error(
    booking: Booking,
) -> None:
    transactions_mock_client = mock.create_autospec(transactions.Client)
    transactions_mock_client.create = mock.AsyncMock(
        side_effect=errors.NotFoundError("Quotation not found"),
    )

    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_mock_client,
    )

    with stdout.capture_logs() as cap_logs:
        with pytest.raises(PayTransactionCreationError):
            await pay_transactions.create_transaction(
                booking=booking,
            )

        assert len(cap_logs) == 1

        for log in cap_logs:
            assert log["pay_quote_id"] == pay_fixtures.QUOTATIONS[0]
            assert log["event"] == "Transaction creation failed"
