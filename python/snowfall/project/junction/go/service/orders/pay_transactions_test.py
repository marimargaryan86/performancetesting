from unittest import mock

import pytest

from snowfall.project.junction.go import fixtures
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
from snowfall.project.pay.adapter import quotations, transactions
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout


@pytest.fixture()
def booking() -> Booking:
    return Booking(
        id=string.uuid(),
        order_id=string.uuid(),
        trip_option=TripOption(pay_quote_id=fixtures.QUOTATIONS[0]),
        status=Booking.Status.STATUS_PENDING,
        provider_name="a-provider",
        total_price=None,
        trip_result=TripBooking(provider_booking_reference="a-provider-reference"),
        raw_data="raw data",
        created_at=None,
        updated_at=None,
        transaction_id="",
    )


async def test_that_transaction_created_and_id_set_in_booking(
    transactions_client: transactions.Client,
    quotations_client: quotations.Client,
    booking: Booking,
) -> None:
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_client,
        quotations_client=quotations_client,
    )

    updated_booking = await pay_transactions.create_transaction_and_set_id(
        booking=booking,
    )

    assert updated_booking.transaction_id


async def test_that_transaction_not_created(
    transactions_client: transactions.Client,
    quotations_client: quotations.Client,
    booking: Booking,
) -> None:
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=False,
        transactions_client=transactions_client,
        quotations_client=quotations_client,
    )

    updated_booking = await pay_transactions.create_transaction_and_set_id(
        booking=booking,
    )

    assert not updated_booking.transaction_id


async def test_quotation_not_found_raises_error(
    transactions_client: transactions.Client,
    quotations_client: quotations.Client,
    booking: Booking,
) -> None:
    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_client,
        quotations_client=quotations_client,
    )

    booking.trip_option.MergeFrom(TripOption(pay_quote_id=fixtures.NOT_FOUND))
    with pytest.raises(PayTransactionCreationError):
        await pay_transactions.create_transaction_and_set_id(
            booking=booking,
        )


async def test_create_transaction_failed_raises_error(
    quotations_client: quotations.Client,
    booking: Booking,
) -> None:
    transactions_client = mock.create_autospec(transactions.Client)
    transactions_client.create = mock.AsyncMock(side_effect=errors.UnhandledError())

    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_client,
        quotations_client=quotations_client,
    )

    with pytest.raises(PayTransactionCreationError):
        await pay_transactions.create_transaction_and_set_id(
            booking=booking,
        )


async def test_update_quotation_status_failed_logs_error(
    transactions_client: transactions.Client,
    booking: Booking,
) -> None:
    quotations_client = mock.create_autospec(quotations.Client)
    quotations_client.get = mock.AsyncMock(return_value=fixtures.get_quotations()[0])
    quotations_client.update_status = mock.AsyncMock(return_value=False)

    pay_transactions = PayTransactionCreator(
        use_pay_to_create_transaction=True,
        transactions_client=transactions_client,
        quotations_client=quotations_client,
    )

    with stdout.capture_logs() as cap_logs:
        await pay_transactions.create_transaction_and_set_id(
            booking=booking,
        )

        assert len(cap_logs) == 1

        for log in cap_logs:
            assert log["pay_quote_id"] == fixtures.QUOTATIONS[0]
            assert log["event"] == "Failed to update quotation status in Pay"
