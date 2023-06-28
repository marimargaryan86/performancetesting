import datetime
from copy import deepcopy
from unittest.mock import create_autospec

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
    TransactionDirectionSchema,
    TransactionPassengerSchema,
    TransactionPostSchema,
)
from snowfall.project.pss.service.pss_api_v2.validators.transaction import (
    TransactionValidator,
)


class TestTransactionValidation:  # noqa: WPS306,WPS214
    _schema = TransactionPostSchema(
        directions={"outbound"},
        channel="desktop",
        outbound=TransactionDirectionSchema(
            date=datetime.datetime.now(tz=datetime.UTC).date(),
            destination_id=0,
            origin_id=0,
        ),
    )
    _transaction_statuses_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _customers_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _accounts_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _bookings_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _agreements_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _schedules_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _products_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _passenger_types_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _seat_types_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    _validator = TransactionValidator(
        _transaction_statuses_repository_mock,
        _customers_repository_mock,
        _accounts_repository_mock,
        _bookings_repository_mock,
        _agreements_repository_mock,
        _schedules_repository_mock,
        _products_repository_mock,
        _passenger_types_repository_mock,
        _seat_types_repository_mock,
    )

    async def test_that_transaction_status_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.transaction_status_id = 1
        self._transaction_statuses_repository_mock.get_one_by_filter.return_value = (
            TransactionStatus(id=1)
        )
        reasons = await self._validator._validate_transaction_status_id(
            to_validate,
        )
        assert not reasons

    async def test_that_transaction_status_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.transaction_status_id = 1
        self._transaction_statuses_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_transaction_status_id(
            to_validate,
        )
        assert (
            reasons[0]
            == "No entry in transaction_statuses for transaction_status_id: 1"
        )

    async def test_that_none_transaction_status_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        reasons = await self._validator._validate_transaction_status_id(
            to_validate,
        )
        assert not reasons

    async def test_that_customer_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.customer_id = 1
        self._customers_repository_mock.get_one_by_filter.return_value = Customer(id=1)
        reasons = await self._validator._validate_customer_id(
            to_validate,
        )
        assert not reasons

    async def test_that_customer_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.customer_id = 1
        self._customers_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_customer_id(
            to_validate,
        )
        assert reasons[0] == "No entry in customers for customer_id: 1"

    async def test_that_none_customer_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        reasons = await self._validator._validate_customer_id(
            to_validate,
        )
        assert not reasons

    async def test_that_account_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.account_id = 1
        self._accounts_repository_mock.get_one_by_filter.return_value = Account(id=1)
        reasons = await self._validator._validate_account_id(
            to_validate,
        )
        assert not reasons

    async def test_that_account_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.account_id = 1
        self._accounts_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_account_id(
            to_validate,
        )
        assert reasons[0] == "No entry in accounts for account_id: 1"

    async def test_that_none_account_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        reasons = await self._validator._validate_account_id(
            to_validate,
        )
        assert not reasons

    async def test_that_booking_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.booking_id = 1
        self._bookings_repository_mock.get_one_by_filter.return_value = Booking(id=1)
        reasons = await self._validator._validate_booking_id(
            to_validate,
        )
        assert not reasons

    async def test_that_booking_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.booking_id = 1
        self._bookings_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_booking_id(
            to_validate,
        )
        assert reasons[0] == "No entry in bookings for booking_id: 1"

    async def test_that_none_booking_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        reasons = await self._validator._validate_booking_id(
            to_validate,
        )
        assert not reasons

    async def test_that_agreement_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.agreement_id = 1
        self._agreements_repository_mock.get_one_by_filter.return_value = Agreement(
            agreementnumber=1,
        )
        reasons = await self._validator._validate_agreement_id(
            to_validate,
        )
        assert not reasons

    async def test_that_agreement_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.agreement_id = 1
        self._agreements_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_agreement_id(
            to_validate,
        )
        assert reasons[0] == "No entry in agreements for agreement_id: 1"

    async def test_that_none_agreement_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        reasons = await self._validator._validate_agreement_id(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_schedule_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
        )
        self._schedules_repository_mock.get_one_by_filter.return_value = Schedule(
            id=1,
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_schedule_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
        )
        self._schedules_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert reasons[0] == "No entry in schedules for outbound.schedule_id: 1"

    async def test_that_none_outbound_schedule_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(destination_id=0, origin_id=0)
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_schedule_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
        )
        self._schedules_repository_mock.get_one_by_filter.return_value = Schedule(
            id=1,
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_schedule_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
        )
        self._schedules_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert reasons[0] == "No entry in schedules for inbound.schedule_id: 1"

    async def test_that_none_inbound_schedule_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(destination_id=0, origin_id=0)
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_product_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            product_id=1,
        )
        self._products_repository_mock.get_one_by_filter.return_value = Product(
            id=1,
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_products_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            product_id=1,
        )
        self._products_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert reasons[0] == "No entry in products for outbound.product_id: 1"

    async def test_that_none_outbound_products_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(destination_id=0, origin_id=0)
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_products_id_that_exists_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            product_id=1,
        )
        self._products_repository_mock.get_one_by_filter.return_value = Product(
            id=1,
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_products_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            product_id=1,
        )
        self._products_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert reasons[0] == "No entry in products for inbound.product_id: 1"

    async def test_that_none_inbound_products_id_validates(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(destination_id=0, origin_id=0)
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_passenger_passenger_type_id_that_exists_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                ),
            ],
        )
        self._passenger_types_repository_mock.get_one_by_filter.return_value = (
            PassengerType(
                id=1,
            )
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_passenger_passenger_type_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                ),
            ],
        )
        self._passenger_types_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert (
            reasons[0]
            == "No entry in passenger_types for"
            " outbound.passengers[0].passenger_type_id: 1"
        )

    async def test_that_none_outbound_passenger_passenger_type_id_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                ),
            ],
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_passenger_passenger_type_id_that_exists_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                ),
            ],
        )
        self._passenger_types_repository_mock.get_one_by_filter.return_value = (
            PassengerType(
                id=1,
            )
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_passenger_passenger_type_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                ),
            ],
        )
        self._passenger_types_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert (
            reasons[0]
            == "No entry in passenger_types for"
            " inbound.passengers[0].passenger_type_id: 1"
        )

    async def test_that_none_inbound_passenger_passenger_type_id_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                ),
            ],
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_passenger_seat_type_id_that_exists_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    seat_type_id=1,
                ),
            ],
        )
        self._seat_types_repository_mock.get_one_by_filter.return_value = SeatType(
            id=1,
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_outbound_passenger_seat_type_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    seat_type_id=1,
                ),
            ],
        )
        self._seat_types_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert (
            reasons[0]
            == "No entry in seat_types for outbound.passengers[0].seat_type_id: 1"
        )

    async def test_that_none_outbound_passenger_seat_type_id_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                ),
            ],
        )
        reasons = await self._validator._validate_outbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_passenger_seat_type_id_that_exists_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    seat_type_id=1,
                ),
            ],
        )
        self._seat_types_repository_mock.get_one_by_filter.return_value = SeatType(
            id=1,
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_inbound_passenger_seat_type_id_that_doesnt_exist_doesnt_validate(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    seat_type_id=1,
                ),
            ],
        )
        self._seat_types_repository_mock.get_one_by_filter.return_value = None
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert (
            reasons[0]
            == "No entry in seat_types for inbound.passengers[0].seat_type_id: 1"
        )

    async def test_that_none_inbound_passenger_seat_type_id_validates(
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                ),
            ],
        )
        reasons = await self._validator._validate_inbound(
            to_validate,
        )
        assert not reasons

    async def test_that_wholly_valid_transaction_has_no_errors(self) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.transaction_status_id = 1
        to_validate.customer_id = 1
        to_validate.account_id = 1
        to_validate.booking_id = 1
        to_validate.agreement_id = 1
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
            product_id=1,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                    seat_type_id=1,
                ),
            ],
        )
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
            product_id=1,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                    seat_type_id=1,
                ),
            ],
        )
        self._transaction_statuses_repository_mock.get_one_by_filter.return_value = (
            TransactionStatus(id=1)
        )
        self._customers_repository_mock.get_one_by_filter.return_value = Customer(id=1)
        self._accounts_repository_mock.get_one_by_filter.return_value = Account(id=1)
        self._bookings_repository_mock.get_one_by_filter.return_value = Booking(id=1)
        self._agreements_repository_mock.get_one_by_filter.return_value = Agreement(
            agreementnumber=1,
        )
        self._schedules_repository_mock.get_one_by_filter.return_value = Schedule(
            id=1,
        )
        self._products_repository_mock.get_one_by_filter.return_value = Product(
            id=1,
        )
        self._passenger_types_repository_mock.get_one_by_filter.return_value = (
            PassengerType(id=1)
        )
        self._seat_types_repository_mock.get_one_by_filter.return_value = SeatType(
            id=1,
        )
        is_valid, reasons = await self._validator.is_valid(to_validate)
        assert is_valid
        assert not reasons

    async def test_that_wholly_invalid_transaction_has_all_errors(  # noqa: WPS218
        self,
    ) -> None:
        to_validate = deepcopy(self._schema)
        to_validate.transaction_status_id = 1
        to_validate.customer_id = 1
        to_validate.account_id = 1
        to_validate.booking_id = 1
        to_validate.agreement_id = 1
        to_validate.outbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
            product_id=1,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                    seat_type_id=1,
                ),
            ],
        )
        to_validate.inbound = TransactionDirectionSchema(
            destination_id=0,
            origin_id=0,
            schedule_id=1,
            product_id=1,
            passengers=[
                TransactionPassengerSchema(
                    seat_id=0,
                    passenger_type_id=PassengerTypeEnum.adult,
                    seat_type_id=1,
                ),
            ],
        )
        self._transaction_statuses_repository_mock.get_one_by_filter.return_value = None
        self._customers_repository_mock.get_one_by_filter.return_value = None
        self._accounts_repository_mock.get_one_by_filter.return_value = None
        self._bookings_repository_mock.get_one_by_filter.return_value = None
        self._agreements_repository_mock.get_one_by_filter.return_value = None
        self._schedules_repository_mock.get_one_by_filter.return_value = None
        self._products_repository_mock.get_one_by_filter.return_value = None
        self._passenger_types_repository_mock.get_one_by_filter.return_value = None
        self._seat_types_repository_mock.get_one_by_filter.return_value = None
        is_valid, reasons = await self._validator.is_valid(to_validate)
        assert not is_valid
        assert (
            "No entry in transaction_statuses for transaction_status_id: 1" in reasons
        )
        assert "No entry in customers for customer_id: 1" in reasons
        assert "No entry in accounts for account_id: 1" in reasons
        assert "No entry in bookings for booking_id: 1" in reasons
        assert "No entry in agreements for agreement_id: 1" in reasons
        assert "No entry in schedules for outbound.schedule_id: 1" in reasons
        assert "No entry in schedules for inbound.schedule_id: 1" in reasons
        assert "No entry in products for outbound.product_id: 1" in reasons
        assert "No entry in products for inbound.product_id: 1" in reasons
        assert (
            "No entry in passenger_types for"
            " outbound.passengers[0].passenger_type_id: 1"
            in reasons
        )
        assert (
            "No entry in passenger_types for inbound.passengers[0].passenger_type_id: 1"
            in reasons
        )
        assert (
            "No entry in seat_types for outbound.passengers[0].seat_type_id: 1"
            in reasons
        )
        assert (
            "No entry in seat_types for inbound.passengers[0].seat_type_id: 1"
            in reasons
        )
