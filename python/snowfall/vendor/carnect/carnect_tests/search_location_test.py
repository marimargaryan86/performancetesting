from snowfall.vendor.carnect.adapters.location_search_adapter import (
    LocationSearchAdapter,
)
from snowfall.vendor.carnect.builders.location_search_builder import (
    LocationSearchRqBuilder,
)
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config


@disable_by_default
async def test_search_location(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = LocationSearchRqBuilder(carnect_config)
    criterion = rq.add_search_criterion()
    criterion.add_geo_point(51.5072, 0.1276)  # noqa: WPS432
    criterion.radius_km(50)  # noqa: WPS432
    criterion.ranking(100)

    rq.pos().add_source().iso_country("GB")

    rs_adapter = LocationSearchAdapter(
        await carnect_client.location_search(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
