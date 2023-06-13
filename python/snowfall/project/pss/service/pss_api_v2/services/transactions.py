from collections.abc import Sequence

from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.transactions import Transaction
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.schemas.transactions import (
    TransactionDirectionSchema,
    TransactionPostSchema,
)
from snowfall.project.pss.service.pss_api_v2.validators.transaction import (
    TransactionValidator,
)


class DuplicateSeatError(Exception):
    """Raised when a Transaction has multiple passengers in the same seat."""


class InvalidTransactionError(Exception):
    def __init__(self, reasons: Sequence[str]):
        self._reasons = reasons

    def reasons(self) -> Sequence[str]:
        return self._reasons


class TransactionService(object):
    _blank_transaction_for_stubbing = TransactionPostSchema(
        directions={"outbound"},
        channel="stubbing",
        outbound=TransactionDirectionSchema(destination_id=-1, origin_id=-1),
    )

    def __init__(
        self,
        repository: Repository[Transaction] = Depends(Repository.factory(Transaction)),
        validator: TransactionValidator = Depends(TransactionValidator),
    ) -> None:
        self._repository = repository
        self._validator = validator

    async def handle_post_transaction(
        self,
        transaction: TransactionPostSchema,
    ) -> TransactionPostSchema:
        if await self._has_multiple_passengers_in_same_seat(transaction):
            raise DuplicateSeatError()
        if transaction.token:
            transaction = await self._process_transaction(transaction)
        else:
            transaction = await self._initialise_transaction(transaction)
        return transaction

    async def _initialise_transaction(
        self,
        transaction: TransactionPostSchema,
    ) -> TransactionPostSchema:
        is_valid, reasons = await self._validator.is_valid(transaction)
        if not is_valid:
            raise InvalidTransactionError(reasons=reasons)
        return self._blank_transaction_for_stubbing

    async def _process_transaction(
        self,
        transaction: TransactionPostSchema,
    ) -> TransactionPostSchema:
        return self._blank_transaction_for_stubbing

    async def _has_multiple_passengers_in_same_seat(  # noqa: WPS210
        self,
        transaction: TransactionPostSchema,
    ) -> bool:
        if transaction.outbound:
            passengers_outbound = transaction.outbound.passengers
        else:
            passengers_outbound = None

        same_seat_outbound = (
            any(
                p1.seat_id == p2.seat_id
                for idx, p1 in enumerate(passengers_outbound)
                for p2 in passengers_outbound[idx + 1 :]
            )
            if passengers_outbound
            else False
        )

        if transaction.inbound:
            passengers_inbound = transaction.inbound.passengers
        else:
            passengers_inbound = None

        same_seat_inbound = (
            any(
                p1.seat_id == p2.seat_id
                for idx, p1 in enumerate(passengers_inbound)
                for p2 in passengers_inbound[idx + 1 :]
            )
            if passengers_inbound
            else False
        )
        return same_seat_outbound or same_seat_inbound
