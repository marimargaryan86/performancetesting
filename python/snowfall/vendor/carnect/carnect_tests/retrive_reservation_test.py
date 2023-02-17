from snowfall.vendor.carnect.adapters.veh_ret_res_adapter import VehRetResAdapter
from snowfall.vendor.carnect.builders.veh_ret_res_builder import VehRetResRqBuilder
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config


@disable_by_default
async def test_retrieve_reservation(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = VehRetResRqBuilder(carnect_config)
    rq.unique_id().id_context("TES650864613204")
    rq.person_name().surname("Test")
    rs_adapter = VehRetResAdapter(await carnect_client.retrieve_reservation(rq.build()))
    assert rs_adapter.is_success(), rs_adapter.get_error()
