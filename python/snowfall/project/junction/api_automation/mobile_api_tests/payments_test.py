import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)


@pytest.mark.integration
async def test_create_payment(mobile_client: MobileApiClient) -> None:
    resp = await with_log(mobile_client.create_payment)(currency="EUR", amount="3.14")
    assert "id" in resp["data"]


@pytest.mark.integration
async def test_update_payment(mobile_client: MobileApiClient) -> None:
    resp = await with_log(mobile_client.create_payment)(currency="EUR", amount="3.14")
    payment_id = resp["data"]["id"]
    status = await with_log(mobile_client.update_payment)(
        payment_intent_id=payment_id,
        voucher_id="ABC12345",
    )
    assert status == 204
