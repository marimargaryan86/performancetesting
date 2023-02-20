import datetime
from typing import Sequence

from snowfall.vendor.carnect.adapters.cancel_reservation_adapter import (
    CancelReservationAdapter,
)
from snowfall.vendor.carnect.adapters.reservation_adapter import ReservationAdapter
from snowfall.vendor.carnect.builders.cancel_reservation_builder import (
    CancelReservationRqBuilder,
)
from snowfall.vendor.carnect.builders.reservation_builder import (
    CustomerPrimaryBuilder,
    ReservationBuilder,
)
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.carnect_tests.conftest import DRIVER_AGE
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    CustomerTypeGender,
    VehicleVendorAvailabilityType,
)


@disable_by_default
async def test_reservation(  # noqa: WPS210
    carnect_client: CarnectClient,
    carnect_config: Config,
    offers: Sequence[VehicleVendorAvailabilityType],
) -> None:
    offer_id_context = _get_test_offer_id_context(offers)
    assert offer_id_context is not None
    res_rq = ReservationBuilder(config=carnect_config)
    res_rq.veh_pref_code(offer_id_context)
    _init_test_driver(res_rq.primary_driver())

    res_adapter = ReservationAdapter(
        await carnect_client.reservation(res_rq),
    )

    assert res_adapter.is_success(), res_adapter.get_error()
    id_context = res_adapter.get_id_context()
    assert id_context is not None

    cancel_rq = _build_cancel_rq(carnect_config, id_context, "Test")
    cancel_adapter = CancelReservationAdapter(
        await carnect_client.cancel_reservation(cancel_rq.build()),
    )
    assert cancel_adapter.is_success(), cancel_adapter.get_error()


def _build_cancel_rq(
    config: Config,
    id_context: str,
    surname: str,
) -> CancelReservationRqBuilder:
    cancel_rq = CancelReservationRqBuilder(conf=config)
    cancel_info = cancel_rq.get_cancel_info_type()
    cancel_info.add_unique_id().id_context(id_context)
    cancel_info.get_person_name().surname(surname)
    return cancel_rq


def _get_test_offer_id_context(
    offers: Sequence[VehicleVendorAvailabilityType],
) -> str | None:
    if offers:
        offer = offers[0]

        if offer.veh_avails and offer.veh_avails.veh_avail:
            veh_avail = offer.veh_avails.veh_avail[0]

            if veh_avail.veh_avail_core and veh_avail.veh_avail_core.reference:
                return veh_avail.veh_avail_core.reference.id_context

    return None


def _init_test_driver(driver: CustomerPrimaryBuilder) -> None:  # noqa: WPS213
    driver.surname("Test")
    driver.given_name("Test")
    driver.email("testcheck@carnect.com")
    age = datetime.timedelta(days=365 * DRIVER_AGE + 150)
    driver.birth_date(
        datetime.datetime.now().date() - age,
    )
    driver.gender(CustomerTypeGender.MALE)
    driver.language("EN")
    driver.add_phone("5141234567")
    driver_addr = driver.add_address()
    driver_addr.street_nmbr("Buceriusstr. 2")
    driver_addr.city_name("Hamburg")
    driver_addr.postal_code("20095")
    driver.citizen_country_code("DE")
