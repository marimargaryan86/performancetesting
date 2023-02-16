import datetime

from snowfall.vendor.carnect.adapters import veh_avail_rate_adapter
from snowfall.vendor.carnect.builders import veh_avail_rate_builder
from snowfall.vendor.carnect.carnect_tests.carnect_test import disable_by_default
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import RateQueryType


@disable_by_default
async def test_avail_rate(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> None:
    rq = veh_avail_rate_builder.VehAvailRateRqBuilder(carnect_config)

    rq.version("large")
    rq.rate_query_type(RateQueryType.LIVE)
    rq.rate_query_parameter_type("4")
    rental_core = rq.get_rental_core()
    rental_core.pick_up_date(datetime.datetime.now() + datetime.timedelta(days=10))
    rental_core.return_date(
        datetime.datetime.now() + datetime.timedelta(days=15),  # noqa: WPS432
    )
    rental_core.add_pick_up_location("LHR", "2")
    rental_core.return_location("LHR", "2")

    rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(
        await carnect_client.get_avail_rate(rq.build()),
    )
    assert rs_adapter.is_success(), rs_adapter.get_error()
