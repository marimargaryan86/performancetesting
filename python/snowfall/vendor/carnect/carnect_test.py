import datetime
import os
from typing import Sequence

import pytest

from snowfall.vendor.carnect import client
from snowfall.vendor.carnect.adapters import (
    cancel_reservation_adapter,
    location_details_adapter,
    location_search_adapter,
    veh_avail_rate_adapter,
    veh_rate_rule_adapter,
)
from snowfall.vendor.carnect.builders import (
    cancel_reservation_builder,
    location_details_builder,
    location_search_builder,
    ping_builder,
    veh_avail_rate_builder,
    veh_rate_rule_builder,
)
from snowfall.vendor.carnect.models.service import (
    RateQueryType,
    VehicleVendorAvailabilityType,
    VehLocationSearchRqTarget,
    VehRateRuleRqTarget,
)

disable_by_default = pytest.mark.skipif(
    os.getenv("CARNECT_TESTS") != "ENABLED",
    reason="To enable set env variable CARNECT_TESTS=ENABLED",
)


@disable_by_default
async def test_ping(carnect_client: client.CarnectClient) -> None:
    rq = ping_builder.PingRqBuilder()
    rq.add_echo("test")
    rs = await carnect_client.ping(rq.build())
    assert rs.ping_rs is not None
    assert rs.ping_rs.echo_data == ["test"]


@disable_by_default
async def test_search_location(carnect_client: client.CarnectClient) -> None:
    rq = location_search_builder.LocationSearchRqBuilder()
    criterion = rq.add_search_criterion()
    criterion.add_geo_point(51.5072, 0.1276)
    criterion.radius_km(50)
    criterion.ranking(100)
    rq.target(target=VehLocationSearchRqTarget.TEST)

    pos_source = rq.pos().add_source()
    pos_source.iso_country("EN")
    pos_source.user_name("CarnectNet")
    pos_source.password("1nK9DFF9")
    rq.pos().add_source().iso_country("GB")

    rs_adapter = location_search_adapter.LocationSearchAdapter(
        await carnect_client.location_search(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()


@disable_by_default
async def test_get_location_details_by_location_code(
    carnect_client: client.CarnectClient,
    carnect_config: client.Config,
) -> None:
    rq = location_details_builder.LocationDetailsRqBuilder(carnect_config)
    rq.location_code("7600868")

    rs_adapter = location_details_adapter.LocationDetailsAdapter(
        await carnect_client.get_location_details(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.location_details() is not None


@disable_by_default
async def test_get_location_details_by_extended_location_code(
    carnect_client: client.CarnectClient,
    carnect_config: client.Config,
) -> None:
    rq = location_details_builder.LocationDetailsRqBuilder(carnect_config)
    rq.extended_location_code("ZEARN")

    rs_adapter = location_details_adapter.LocationDetailsAdapter(
        await carnect_client.get_location_details(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.location_details() is not None


@disable_by_default
async def test_avail_rate(carnect_client: client.CarnectClient) -> None:
    rq = veh_avail_rate_builder.VehAvailRateRqBuilder()

    pos_source = rq.pos().add_source()
    pos_source.iso_country("EN")
    pos_source.user_name("CarnectNet")
    pos_source.password("1nK9DFF9")

    rq.rate_query_type(RateQueryType.LIVE)
    rq.rate_query_parameter_type("4")
    rental_core = rq.get_rental_core()
    rental_core.pick_up_date(datetime.datetime.now() + datetime.timedelta(days=10))
    rental_core.return_date(datetime.datetime.now() + datetime.timedelta(days=15))
    rental_core.add_pick_up_location("LHR", "2")
    rental_core.return_location("LHR", "2")

    rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(
        await carnect_client.get_avail_rate(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()


@disable_by_default
async def test_rate_rule(
    carnect_client: client.CarnectClient,
    offers: Sequence[VehicleVendorAvailabilityType],
) -> None:
    assert offers
    offer = offers[0]
    rule_rq = veh_rate_rule_builder.VehRateRuleRqBuilder()

    pos_source = rule_rq.pos().add_source()
    pos_source.user_name("CarnectNet")
    pos_source.password("1nK9DFF9")

    rule_rq.target(VehRateRuleRqTarget.TEST)
    assert offer.veh_avails and offer.veh_avails.veh_avail
    veh_avail = offer.veh_avails.veh_avail[0]
    assert veh_avail.veh_avail_core and veh_avail.veh_avail_core.reference

    rule_rq.reference(veh_avail.veh_avail_core.reference.id_context or "")

    rule_adapter = veh_rate_rule_adapter.VehRateRuleAdapter(
        await carnect_client.veh_rate_rules(rule_rq.build()),
    )
    assert rule_adapter.is_success(), rule_adapter.get_error()


@disable_by_default
async def test_cancel_reservation_by_unique_context_id(
    carnect_client: client.CarnectClient,
    carnect_config: client.Config,
) -> None:
    rq = cancel_reservation_builder.CancelReservationRqBuilder(carnect_config)
    cancel_info_type = rq.get_cancel_info_type()
    unique_id = cancel_info_type.add_unique_id()
    unique_id.id_context("MN0929384X0")

    rs_adapter = cancel_reservation_adapter.CancelReservationAdapter(
        await carnect_client.cancel_reservation(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.cancel_info() is not None


@disable_by_default
async def test_cancel_reservation_by_unique_id_and_surname(
    carnect_client: client.CarnectClient,
    carnect_config: client.Config,
) -> None:
    rq = cancel_reservation_builder.CancelReservationRqBuilder(carnect_config)
    cancel_info_type = rq.get_cancel_info_type()
    unique_id = cancel_info_type.add_unique_id()
    unique_id.unique_id("0X129302B4")
    unique_id.unique_id_type("14")
    person_name = cancel_info_type.get_person_name()
    person_name.surname("Jones")

    rs_adapter = cancel_reservation_adapter.CancelReservationAdapter(
        await carnect_client.cancel_reservation(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.cancel_info() is not None
