from typing import Sequence

from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.models.agreements import Agreement
from snowfall.project.pss.service.pss_api_v2.db.models.bookings import Booking
from snowfall.project.pss.service.pss_api_v2.db.models.customers import Customer
from snowfall.project.pss.service.pss_api_v2.db.models.passenger_types import (
    PassengerType,
)
from snowfall.project.pss.service.pss_api_v2.db.models.products import Product
from snowfall.project.pss.service.pss_api_v2.db.models.schedules import Schedule
from snowfall.project.pss.service.pss_api_v2.db.models.seat_types import SeatType
from snowfall.project.pss.service.pss_api_v2.db.models.transactions import (
    TransactionStatus,
)
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.schemas.transactions import (
    PassengerType as PassengerTypeEnum,
)
from snowfall.project.pss.service.pss_api_v2.schemas.transactions import (
    TransactionPassengerSchema,
    TransactionPostSchema,
)
from snowfall.project.pss.service.pss_api_v2.validators.validator import Validator


class TransactionValidator(Validator[TransactionPostSchema]):  # noqa:WPS214
    def __init__(  # noqa:WPS211
        self,
        transaction_statuses_repository: Repository[TransactionStatus] = Depends(
            Repository.factory(TransactionStatus),
        ),
        customers_repository: Repository[Customer] = Depends(
            Repository.factory(Customer),
        ),
        accounts_repository: Repository[Account] = Depends(Repository.factory(Account)),
        bookings_repository: Repository[Booking] = Depends(Repository.factory(Booking)),
        agreements_repository: Repository[Agreement] = Depends(
            Repository.factory(Agreement),
        ),
        schedules_repository: Repository[Schedule] = Depends(
            Repository.factory(Schedule),
        ),
        products_repository: Repository[Product] = Depends(
            Repository.factory(Product),
        ),
        passenger_types_repository: Repository[PassengerType] = Depends(
            Repository.factory(PassengerType),
        ),
        seat_types_repository: Repository[SeatType] = Depends(
            Repository.factory(SeatType),
        ),
    ) -> None:
        self._transaction_statuses_repository = transaction_statuses_repository
        self._customers_repository = customers_repository
        self._accounts_repository = accounts_repository
        self._bookings_repository = bookings_repository
        self._agreements_repository = agreements_repository
        self._schedules_repository = schedules_repository
        self._products_repository = products_repository
        self._passenger_types_repository = passenger_types_repository
        self._seat_types_repository = seat_types_repository

    async def is_valid(  # noqa:WPS217
        self,
        to_validate: TransactionPostSchema,
    ) -> tuple[bool, list[str]]:
        reasons = [
            *await self._validate_transaction_status_id(to_validate),
            *await self._validate_customer_id(to_validate),
            *await self._validate_account_id(to_validate),
            *await self._validate_booking_id(to_validate),
            *await self._validate_agreement_id(to_validate),
            *await self._validate_outbound(to_validate),
            *await self._validate_inbound(to_validate),
        ]
        is_valid = not reasons
        return is_valid, reasons

    async def _validate_transaction_status_id(
        self,
        to_validate: TransactionPostSchema,
    ) -> list[str]:
        if to_validate.transaction_status_id is not None:
            entry = await self._transaction_statuses_repository.get_one_by_filter(
                [TransactionStatus.id == to_validate.transaction_status_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in transaction_statuses "
                    + "for transaction_status_id: {0}".format(
                        to_validate.transaction_status_id,
                    ),
                ]
            )
        return []

    async def _validate_customer_id(
        self,
        to_validate: TransactionPostSchema,
    ) -> list[str]:
        if to_validate.customer_id is not None:
            entry = await self._customers_repository.get_one_by_filter(
                [Customer.id == to_validate.customer_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in customers for customer_id: {0}".format(
                        to_validate.customer_id,
                    ),
                ]
            )
        return []

    async def _validate_account_id(
        self,
        to_validate: TransactionPostSchema,
    ) -> list[str]:
        if to_validate.account_id is not None:
            entry = await self._accounts_repository.get_one_by_filter(
                [Account.id == to_validate.account_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in accounts for account_id: {0}".format(
                        to_validate.account_id,
                    ),
                ]
            )
        return []

    async def _validate_booking_id(
        self,
        to_validate: TransactionPostSchema,
    ) -> list[str]:
        if to_validate.booking_id is not None:
            entry = await self._bookings_repository.get_one_by_filter(
                [Booking.id == to_validate.booking_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in bookings for booking_id: {0}".format(
                        to_validate.booking_id,
                    ),
                ]
            )
        return []

    async def _validate_agreement_id(
        self,
        to_validate: TransactionPostSchema,
    ) -> list[str]:
        if to_validate.agreement_id is not None:
            entry = await self._agreements_repository.get_one_by_filter(
                [Agreement.agreementnumber == to_validate.agreement_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in agreements for agreement_id: {0}".format(
                        to_validate.agreement_id,
                    ),
                ]
            )
        return []

    async def _validate_schedule_id(
        self,
        direction: str,
        schedule_id: int | None,
    ) -> list[str]:
        if schedule_id is not None:
            entry = await self._schedules_repository.get_one_by_filter(
                [Schedule.id == schedule_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in schedules for {0}.schedule_id: {1}".format(
                        direction,
                        schedule_id,
                    ),
                ]
            )
        return []

    async def _validate_product_id(
        self,
        direction: str,
        product_id: int | None,
    ) -> list[str]:
        if product_id is not None:
            entry = await self._products_repository.get_one_by_filter(
                [Product.id == product_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in products for {0}.product_id: {1}".format(
                        direction,
                        product_id,
                    ),
                ]
            )
        return []

    async def _validate_passenger_type_id(
        self,
        direction: str,
        idx: int,
        passenger_type_id: PassengerTypeEnum | None,
    ) -> list[str]:
        if passenger_type_id is not None:
            entry = await self._passenger_types_repository.get_one_by_filter(
                [PassengerType.id == passenger_type_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in passenger_types for"
                    + " {0}.passengers[{1}].passenger_type_id: {2}".format(
                        direction,
                        idx,
                        int(passenger_type_id),
                    ),
                ]
            )
        return []

    async def _validate_seat_type_id(
        self,
        direction: str,
        idx: int,
        seat_type_id: int | None,
    ) -> list[str]:
        if seat_type_id is not None:
            entry = await self._seat_types_repository.get_one_by_filter(
                [SeatType.id == seat_type_id],
            )
            return (
                []
                if entry
                else [
                    "No entry in seat_types for"
                    + " {0}.passengers[{1}].seat_type_id: {2}".format(
                        direction,
                        idx,
                        int(seat_type_id),
                    ),
                ]
            )
        return []

    async def _validate_passengers(
        self,
        direction: str,
        to_validate: Sequence[TransactionPassengerSchema],
    ) -> list[str]:
        issues = []
        for idx, passenger in enumerate(to_validate):
            issues.extend(
                await self._validate_passenger_type_id(
                    direction,
                    idx,
                    passenger.passenger_type_id,
                ),
            )
            issues.extend(
                await self._validate_seat_type_id(
                    direction,
                    idx,
                    passenger.seat_type_id,
                ),
            )
        return issues

    async def _validate_outbound(self, to_validate: TransactionPostSchema) -> list[str]:
        if to_validate.outbound:
            return [
                *await self._validate_schedule_id(
                    "outbound",
                    to_validate.outbound.schedule_id,
                ),
                *await self._validate_product_id(
                    "outbound",
                    to_validate.outbound.product_id,
                ),
                *await self._validate_passengers(
                    "outbound",
                    to_validate.outbound.passengers,
                ),
            ]
        return []

    async def _validate_inbound(self, to_validate: TransactionPostSchema) -> list[str]:
        if to_validate.inbound:
            return [
                *await self._validate_schedule_id(
                    "inbound",
                    to_validate.inbound.schedule_id,
                ),
                *await self._validate_product_id(
                    "inbound",
                    to_validate.inbound.product_id,
                ),
                *await self._validate_passengers(
                    "inbound",
                    to_validate.inbound.passengers,
                ),
            ]
        return []
