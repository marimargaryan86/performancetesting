from unittest.mock import create_autospec

import pytest

from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.schemas.transactions import (
    PassengerType,
    TransactionDirectionSchema,
    TransactionPassengerSchema,
    TransactionPostSchema,
)
from snowfall.project.pss.service.pss_api_v2.services.transactions import (
    DuplicateSeatError,
    TransactionService,
)


async def test_that_handle_post_transaction_throws_exception_when_multiple_passengers_in_same_seat_in_outbound() -> None:  # noqa:B950
    transaction_with_multiple_passengers_in_outbound_seat = TransactionPostSchema(
        directions={"outbound"},
        channel="desktop",
        outbound=TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    passenger_type_id=PassengerType.adult,
                    seat_id=0,
                ),
                TransactionPassengerSchema(
                    passenger_type_id=PassengerType.adult,
                    seat_id=0,
                ),
            ],
        ),
    )
    mock_transaction_repository = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    transaction_service = TransactionService(repository=mock_transaction_repository)
    with pytest.raises(DuplicateSeatError):
        await transaction_service.handle_post_transaction(
            transaction_with_multiple_passengers_in_outbound_seat,
        )


async def test_that_handle_post_transaction_throws_exception_when_multiple_passengers_in_same_seat_in_inbound() -> None:  # noqa:B950
    transaction_with_multiple_passengers_in_inbound_seat = TransactionPostSchema(
        directions={"inbound"},
        channel="desktop",
        inbound=TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    passenger_type_id=PassengerType.adult,
                    seat_id=0,
                ),
                TransactionPassengerSchema(
                    passenger_type_id=PassengerType.adult,
                    seat_id=0,
                ),
            ],
        ),
    )
    mock_transaction_repository = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    transaction_service = TransactionService(repository=mock_transaction_repository)
    with pytest.raises(DuplicateSeatError):
        await transaction_service.handle_post_transaction(
            transaction_with_multiple_passengers_in_inbound_seat,
        )
