from typing import Sequence

from snowfall.vendor.carnect.adapters.veh_rate_rule_adapter import VehRateRuleAdapter
from snowfall.vendor.carnect.builders.veh_rate_rule_builder import VehRateRuleRqBuilder
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import VehicleVendorAvailabilityType


@disable_by_default
async def test_rate_rule(
    carnect_client: CarnectClient,
    carnect_config: Config,
    offers: Sequence[VehicleVendorAvailabilityType],
) -> None:
    assert offers
    offer = offers[0]
    rule_rq = VehRateRuleRqBuilder(carnect_config)

    assert offer.veh_avails and offer.veh_avails.veh_avail
    veh_avail = offer.veh_avails.veh_avail[0]
    assert veh_avail.veh_avail_core and veh_avail.veh_avail_core.reference

    rule_rq.reference(veh_avail.veh_avail_core.reference.id_context or "")

    rule_adapter = VehRateRuleAdapter(
        await carnect_client.veh_rate_rules(rule_rq.build()),
    )
    assert rule_adapter.is_success(), rule_adapter.get_error()

    assert rule_adapter.priced_equipments()[
        0
    ].equipment_type(), rule_adapter.priced_equipments()[0].description()
