import logging

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import get_variable_value
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_existing_user(
    pay_admin_client: PayAdminClient,
    host: str,
    api_token: str,
) -> None:
    with pytest.raises(httpx.HTTPStatusError) as err:
        await pay_admin_client.create_user(
            email=get_variable_value(host, api_token, "pay_api_test_email"),
            password=get_variable_value(host, api_token, "pay_api_test_password"),
        )
    error = err.value  # noqa: WPS441

    logger.info("response_create_user err headers: %s", error.response.headers)
    logger.info("response_create_user body: %s", error.response.json())

    first_error = error.response.json()["errors"][0]
    assert first_error["status"] == "403"
    assert first_error["code"] == "forbidden"
    assert first_error["detail"] == "User already exists"
    assert first_error["source"]["pointer"] == "/data/id"
