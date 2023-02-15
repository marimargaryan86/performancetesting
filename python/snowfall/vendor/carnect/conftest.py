import datetime
from typing import Any, List

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.carnect import client, config
from snowfall.vendor.carnect.adapters.veh_avail_rate_adapter import VehAvailRateAdapter
from snowfall.vendor.carnect.builders.veh_avail_rate_builder import (
    VehAvailRateRqBuilder,
)
from snowfall.vendor.carnect.models.service import (
    RateQueryType,
    VehicleVendorAvailabilityType,
)

TIMEOUT = 50
RENT_PERIOD_DAYS = 2
PICKUP_DATE_IN_DAYS = 30
NOON_HOURS = 12
API_BASE_URL = "https://ota2007a.micronnexus-staging.com/service.asmx"
HASH = "1nK9DFF9"


@pytest.fixture
def carnect_config() -> config.Config:
    return config.Config(
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
    carnect_config: config.Config,
) -> client.CarnectClient:
    return client.CarnectClient(http_client=http_client, config=carnect_config)


@pytest.fixture
async def offers(
    carnect_client: client.CarnectClient,
) -> List[VehicleVendorAvailabilityType]:
    rq = VehAvailRateRqBuilder()

    pos_source = rq.pos().add_source()
    pos_source.user_name("CarnectNet")
    pos_source.password("1nK9DFF9")

    rq.rate_query_type(RateQueryType.LIVE)
    rq.rate_query_parameter_type("4")
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


def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.distribusion.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    with open(file_path) as json_file:
        return json_util.loads(json_file.read())
