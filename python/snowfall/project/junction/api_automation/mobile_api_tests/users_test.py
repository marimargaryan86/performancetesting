import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)


@pytest.mark.skip(reason="temporary skipped")
async def test_create_users(mobile_client: MobileApiClient) -> None:
    resp = await mobile_client.create_users(
        first_name="John",
        last_name="Weak",
        password="Snowfall",
        email="arega_y@snowfalltravel.com",
        phone="+123456789",
    )
    user_id = resp["data"]["id"]

    assert user_id


@pytest.mark.skip(reason="temporary skipped")
async def test_create_users_session(mobile_client: MobileApiClient) -> None:
    resp = await mobile_client.create_users_session(
        password="Snowfall",
        email="arega_y@snowfalltravel.com",
    )
    user_session_id = resp["data"]["id"]

    assert user_session_id


@pytest.mark.skip(reason="temporary skipped")
async def test_create_verification_code(mobile_client: MobileApiClient) -> None:
    resp = await mobile_client.create_verification_code(
        email="arega_y@snowfalltravel.com",
    )
    verification_code = resp["data"]["id"]

    assert verification_code


@pytest.mark.skip(reason="temporary skipped")
async def test_verification_code_status(mobile_client: MobileApiClient) -> None:
    resp = await with_log(mobile_client.get_verification_code)(
        email="arega_y@snowfalltravel.com",
    )

    verification_code = resp["data"]["id"]

    assert verification_code


@pytest.mark.skip(reason="temporary skipped")
async def test_update_password(mobile_client: MobileApiClient) -> None:
    user_id = "???"
    resp = await mobile_client.update_password(
        email="arega_y@snowfalltravel.com",
        password="123",
        user_id=user_id,
    )
    assert resp["data"]["id"] == user_id


@pytest.mark.skip(reason="temporary skipped")
async def test_update_user(mobile_client: MobileApiClient) -> None:
    user_id = "???"
    resp = await mobile_client.update_user(
        phone="+1233212133",
        gender="male",
        last_name="Smith",
    )
    assert resp["data"]["id"] == user_id
    assert resp["data"]["last_name"] == "Smith"
