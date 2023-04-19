import datetime
import logging
from typing import Any, Mapping

import pytest
from dateutil.parser import parse as datetime_parse

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration()
async def test_get_conversion_details(
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    pay_create_transaction: Mapping[str, Any],
) -> None:
    conversion = pay_create_transaction["data"]["relationships"]["conversion"]["data"]
    conversion_id = conversion["id"]
    response = await pay_admin_client.get_conversion_details(
        conversion_id,
    )

    assert response["data"]["id"] == conversion_id
    assert is_valid_uuid(response["data"]["id"])
    assert response["data"]["type"] == "conversions"
    assert isinstance(response["data"]["attributes"]["rate"], float)
    assert isinstance(
        datetime_parse(
            response["data"]["attributes"]["settledAt"],
        ),
        datetime.date,
    )
