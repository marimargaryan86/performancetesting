import json
import re
import types
from collections.abc import Awaitable, Callable, Collection, Mapping, Sequence
from typing import Any, NewType, TypeAlias

import pydantic
from starlette import requests, responses, status
from starlette.exceptions import HTTPException
from starlette.middleware import base

from snowfall.stdlib.integration.starlette.authentication import AuthenticatedUser

_Record: TypeAlias = pydantic.BaseModel
_Filters: TypeAlias = tuple[str, list[object]]
_Attributes: TypeAlias = dict[str, _Filters]
UserPermissions = NewType("UserPermissions", dict[str, _Attributes])

_PERMISSION_MAPPING = types.MappingProxyType(
    {
        "snowfall-admin": ("*",),
        "snowfall-user": (
            "journey.view",
            "order.view",
            "booking.view",
            "cancel.*",
            "refund.*",
            "transaction.*",
        ),
        "reseller-admin": (
            "journey.*",
            "order.*",
            "booking.*",
            "cancel.add",
            "cancel.view",
            "refund.view",
            "user.*",
        ),
        "reseller-user": (
            "journey.*",
            "order.*",
            "booking.*",
            "cancel.add",
            "cancel.view",
            "refund.view",
        ),
    },
)


class PermissionsMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if isinstance(request.user, AuthenticatedUser):
            request.user.permissions.update(
                permissions_from_user(request.user.metadata),
            )

        return await call_next(request)


def permissions_from_user(
    user_metadata: Mapping[str, Any],
) -> UserPermissions:
    role = user_metadata.get("role", "")
    permissions = _PERMISSION_MAPPING.get(role, ())
    if not role.startswith("snowfall"):
        permissions = tuple(
            '{0}|attributes.resellerId~"{1}"'.format(
                perm,
                user_metadata.get("reseller_id", ""),
            )
            for perm in permissions
        )
    return _permissions_as_dict(permissions)


def _permissions_as_dict(
    permissions: Collection[str],
) -> UserPermissions:
    p_dict: dict[str, _Attributes] = {}
    for permission in permissions:
        perm, *filters = permission.split("|")
        p_dict[perm] = {}
        for filt in filters:
            key, op, filter_val = re.split("(=|~)", filt, maxsplit=1)
            p_dict[perm].setdefault(key, (op, []))[1].append(
                json.loads(filter_val),
            )
    return UserPermissions(p_dict)


def check_permission(
    requested_action: str,
    permissions: UserPermissions,
    context: _Record | None = None,
) -> None:
    if not _has_permission(requested_action, permissions, context):
        raise HTTPException(status.HTTP_403_FORBIDDEN)


def filter_by_permissions(
    resource: str,
    perm_type: str,
    user_perms: UserPermissions,
    record: _Record,
    original: _Record | None = None,
) -> _Record:
    """Return a filtered record containing permissible fields only."""
    filtered_result = {
        record_key: record_value
        for record_key, record_value in record
        if _has_permission(
            "{0}.{1}.{2}".format(resource, record_key, perm_type),
            user_perms,
            context=original or record,
        )
    }
    return record.model_construct(**filtered_result)


def _has_permission(
    requested_action: str,
    permissions: UserPermissions,
    context: _Record | None,
) -> bool:
    *parts, ptype = requested_action.split(".")
    if not _negative_check(permissions, parts, ptype):
        return False

    return _positive_check(permissions, parts, ptype, context)


def _negative_check(
    permissions: UserPermissions,
    parts: Sequence[str],
    ptypes: str,
) -> bool:
    for part in range(len(parts), -1, -1):
        for ptype in (ptypes, "*"):
            perm = ".".join((*parts[:part], ptype))
            if "{0}{1}".format("~", perm) in permissions:
                return False

    return True


def _positive_check(
    permissions: UserPermissions,
    parts: Sequence[str],
    part_types: str,
    context: _Record | None,
) -> bool:
    for part in range(len(parts), -1, -1):
        for part_type in (part_types, "*"):
            perm = ".".join((*parts[:part], part_type))
            if perm in permissions:
                if not context:
                    return True

                return _check_filters(perm, permissions, context)

    return False


def _check_filters(  # noqa: WPS231
    perm: str,
    permissions: UserPermissions,
    context: _Record | None,
) -> bool:
    filters = permissions[perm]
    for attr, (op, filter_vals) in filters.items():
        obj_attribute: object = context
        for resource in attr.split("."):
            if isinstance(obj_attribute, Mapping):
                obj_attribute = obj_attribute.get(resource)
            else:
                obj_attribute = getattr(obj_attribute, resource, None)
        if op == "=" and obj_attribute not in filter_vals:
            return False
        if op == "~" and not set(obj_attribute).intersection(filter_vals):  # type: ignore[call-overload]
            return False
    return True
