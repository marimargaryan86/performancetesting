from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest
from starlette.exceptions import HTTPException

from snowfall.project.junction.hub.service.hub_api import permissions


@pytest.fixture()
def snowfall_admin_permissions() -> permissions.UserPermissions:
    user_metadata = {"reseller_id": "mock", "role": "snowfall-admin"}

    return permissions.permissions_from_user(user_metadata)


@pytest.fixture()
def snowfall_user_permissions() -> permissions.UserPermissions:
    user_metadata = {"reseller_id": "mock", "role": "snowfall-user"}

    return permissions.permissions_from_user(user_metadata)


@pytest.fixture()
def reseller_admin_permissions() -> permissions.UserPermissions:
    user_metadata = {"reseller_id": "mock", "role": "reseller-admin"}

    return permissions.permissions_from_user(user_metadata)


@pytest.fixture()
def reseller_user_permissions() -> permissions.UserPermissions:
    user_metadata = {"reseller_id": "mock", "role": "reseller-user"}

    return permissions.permissions_from_user(user_metadata)


class TestCheckPermissions(object):
    @pytest.mark.parametrize(
        ("action", "expectation"),
        [
            ("booking.view", does_not_raise()),
            ("booking.add", does_not_raise()),
            ("booking.edit", does_not_raise()),
            ("cancel.view", does_not_raise()),
            ("cancel.add", does_not_raise()),
            ("cancel.edit", does_not_raise()),
            ("refund.view", does_not_raise()),
            ("refund.add", does_not_raise()),
            ("refund.edit", does_not_raise()),
            ("user.view", does_not_raise()),
            ("user.add", does_not_raise()),
            ("user.edit", does_not_raise()),
            ("pay.view", does_not_raise()),
            ("pay.add", does_not_raise()),
            ("pay.edit", does_not_raise()),
        ],
    )
    async def test_check_permissions_snowfall_admin(
        self,
        snowfall_admin_permissions: permissions.UserPermissions,
        action: str,
        expectation: Any,
    ) -> None:
        with expectation:
            permissions.check_permission(action, snowfall_admin_permissions)

    @pytest.mark.parametrize(
        ("action", "expectation"),
        [
            ("booking.view", does_not_raise()),
            ("booking.add", does_not_raise()),
            ("booking.edit", does_not_raise()),
            ("cancel.view", does_not_raise()),
            ("cancel.add", does_not_raise()),
            ("cancel.edit", does_not_raise()),
            ("refund.view", does_not_raise()),
            ("refund.add", does_not_raise()),
            ("refund.edit", does_not_raise()),
            ("user.view", pytest.raises(HTTPException)),
            ("user.add", pytest.raises(HTTPException)),
            ("user.edit", pytest.raises(HTTPException)),
            ("pay.view", does_not_raise()),
            ("pay.add", does_not_raise()),
            ("pay.edit", does_not_raise()),
        ],
    )
    async def test_check_permissions_snowfall_user(
        self,
        snowfall_user_permissions: permissions.UserPermissions,
        action: str,
        expectation: Any,
    ) -> None:
        with expectation:
            permissions.check_permission(action, snowfall_user_permissions)

    @pytest.mark.parametrize(
        ("action", "expectation"),
        [
            ("booking.view", does_not_raise()),
            ("booking.add", does_not_raise()),
            ("booking.edit", does_not_raise()),
            ("cancel.view", does_not_raise()),
            ("cancel.add", does_not_raise()),
            ("cancel.edit", pytest.raises(HTTPException)),
            ("refund.view", does_not_raise()),
            ("refund.add", pytest.raises(HTTPException)),
            ("refund.edit", pytest.raises(HTTPException)),
            ("user.view", does_not_raise()),
            ("user.add", does_not_raise()),
            ("user.edit", does_not_raise()),
            ("pay.view", pytest.raises(HTTPException)),
            ("pay.add", pytest.raises(HTTPException)),
            ("pay.edit", pytest.raises(HTTPException)),
        ],
    )
    async def test_check_permissions_reseller_admin(
        self,
        reseller_admin_permissions: permissions.UserPermissions,
        action: str,
        expectation: Any,
    ) -> None:
        with expectation:
            permissions.check_permission(action, reseller_admin_permissions)

    @pytest.mark.parametrize(
        ("action", "expectation"),
        [
            ("booking.view", does_not_raise()),
            ("booking.add", does_not_raise()),
            ("booking.edit", does_not_raise()),
            ("cancel.view", does_not_raise()),
            ("cancel.add", does_not_raise()),
            ("cancel.edit", pytest.raises(HTTPException)),
            ("refund.view", does_not_raise()),
            ("refund.add", pytest.raises(HTTPException)),
            ("refund.edit", pytest.raises(HTTPException)),
            ("user.view", pytest.raises(HTTPException)),
            ("user.add", pytest.raises(HTTPException)),
            ("user.edit", pytest.raises(HTTPException)),
            ("pay.view", pytest.raises(HTTPException)),
            ("pay.add", pytest.raises(HTTPException)),
            ("pay.edit", pytest.raises(HTTPException)),
        ],
    )
    async def test_check_permissions_reseller_user(
        self,
        reseller_user_permissions: permissions.UserPermissions,
        action: str,
        expectation: Any,
    ) -> None:
        with expectation:
            permissions.check_permission(action, reseller_user_permissions)

    async def test_negative_permissions(
        self,
    ) -> None:
        test_permissions = permissions.UserPermissions({"~booking.*": {}})
        with pytest.raises(HTTPException):
            permissions.check_permission("booking.view", test_permissions)
