import datetime
from typing import List

import httpx
import pytest

from snowfall.vendor.carnect.adapters.veh_avail_rate_adapter import VehAvailRateAdapter
from snowfall.vendor.carnect.builders.veh_avail_rate_builder import (
    VehAvailRateRqBuilder,
)
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    RateQueryType,
    VehicleVendorAvailabilityType,
)

TIMEOUT = 50
RENT_PERIOD_DAYS = 2
PICKUP_DATE_IN_DAYS = 30
DRIVER_AGE = 40
NOON_HOURS = 12
API_BASE_URL = "https://ota2007a.micronnexus-staging.com/service.asmx"
HASH = "1nK9DFF9"


@pytest.fixture
def carnect_config() -> Config:
    return Config(
        timeout=TIMEOUT,
        base_url=API_BASE_URL,
        export_soap_requests=True,
        password=HASH,
        is_test=True,
    )


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT)


@pytest.fixture
def carnect_client(
    http_client: httpx.AsyncClient,
    carnect_config: Config,
) -> CarnectClient:
    return CarnectClient(http_client=http_client, config=carnect_config)


@pytest.fixture
async def offers(
    carnect_client: CarnectClient,
    carnect_config: Config,
) -> List[VehicleVendorAvailabilityType]:
    rq = VehAvailRateRqBuilder(carnect_config)

    rq.version("large")
    rq.rate_query_type(RateQueryType.LIVE)
    rq.rate_query_parameter_type("4")
    rq.add_driver_age(DRIVER_AGE)
    rental_core = rq.get_rental_core()
    pickup_datetime = datetime.datetime.combine(
        datetime.datetime.now().date() + datetime.timedelta(days=PICKUP_DATE_IN_DAYS),
        datetime.time(hour=NOON_HOURS),
    )
    rental_core.pick_up_date(pickup_datetime)
    rental_core.return_date(pickup_datetime + datetime.timedelta(days=RENT_PERIOD_DAYS))
    rental_core.add_pick_up_location("LHR", "2")
    rental_core.return_location("LHR", "2")

    rs_adapter = VehAvailRateAdapter(await carnect_client.get_avail_rate(rq.build()))
    assert rs_adapter.is_success(), rs_adapter.get_error()
    return rs_adapter.available()
