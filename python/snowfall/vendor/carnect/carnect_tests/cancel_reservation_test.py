from snowfall.vendor.carnect.adapters.cancel_reservation_adapter import (
    CancelReservationAdapter,
)
from snowfall.vendor.carnect.builders.cancel_reservation_builder import (
    CancelReservationRqBuilder,
)
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config


@disable_by_default
async def test_cancel_by_unique_id(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = CancelReservationRqBuilder(carnect_config)
    cancel_info_type = rq.get_cancel_info_type()
    unique_id = cancel_info_type.add_unique_id()
    unique_id.unique_id("0X129302B4")
    unique_id.unique_id_type("14")
    person_name = cancel_info_type.get_person_name()
    person_name.surname("Jones")

    rs_adapter = CancelReservationAdapter(
        await carnect_client.cancel_reservation(rq),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.cancel_info() is not None


@disable_by_default
async def test_cancel_by_id_context(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = CancelReservationRqBuilder(carnect_config)
    cancel_info_type = rq.get_cancel_info_type()
    unique_id = cancel_info_type.add_unique_id()
    unique_id.id_context("TES650864613204")
    cancel_info_type.get_person_name().surname("Test")

    rs_adapter = CancelReservationAdapter(
        await carnect_client.cancel_reservation(rq),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.cancel_info() is not None
