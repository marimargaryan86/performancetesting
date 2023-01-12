import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)


@pytest.mark.integration
async def test_create_users_groups(
    mobile_client: MobileApiClient,
) -> None:
    group_id = await _return_new_group_id(mobile_client)
    await _update_group(group_id, mobile_client)
    await _delete_group(group_id, mobile_client)


async def _return_new_group_id(mobile_client: MobileApiClient) -> str:
    r1 = await with_log(mobile_client.create_users_groups)(group_name="test_group")
    group_id = r1["data"]["id"]
    resp = await with_log(mobile_client.get_user_group)(group_id=group_id)
    assert resp["data"]["name"] == "test_group"
    return group_id


async def _update_group(group_id: str, mobile_client: MobileApiClient) -> None:
    await with_log(mobile_client.update_trip_group)(
        group_id=group_id,
        group_name="newname",
    )
    resp = await with_log(mobile_client.get_user_group)(group_id=group_id)
    assert resp["data"]["name"] == "newname"


async def _delete_group(group_id: str, mobile_client: MobileApiClient) -> None:
    await with_log(mobile_client.delete_user_group)(group_id=group_id)
    with pytest.raises(HTTPStatusError):
        await with_log(mobile_client.get_user_group)(group_id=group_id)
