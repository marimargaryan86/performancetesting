from snowfall.vendor.carnect.adapters.location_details_adapter import (
    LocationDetailsAdapter,
)
from snowfall.vendor.carnect.builders.location_details_builder import (
    LocationDetailsRqBuilder,
)
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config


@disable_by_default
async def test_get_location_details_by_location_code(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = LocationDetailsRqBuilder(carnect_config)
    rq.location_code("7600868")

    rs_adapter = LocationDetailsAdapter(
        await carnect_client.get_location_details(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.location_details() is not None


@disable_by_default
async def test_get_location_details_by_extended_location_code(  # noqa: WPS118
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = LocationDetailsRqBuilder(carnect_config)
    rq.extended_location_code("ZEARN")

    rs_adapter = LocationDetailsAdapter(
        await carnect_client.get_location_details(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
    assert rs_adapter.location_details() is not None
