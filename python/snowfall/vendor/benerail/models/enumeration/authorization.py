from datetime import date

from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class RcodeAuthorizationGroup(BenerailBaseModel):
    last_update_at: date | None = Field(None, example="2020-10-25")
    identifier: float | None = Field(None, alias="id")
    name: str | None = None
    description: str | None = None


class RcodeAuthorizationAuthorizationGroup(BenerailBaseModel):
    name: str | None = None
    href: str | None = None


class RcodeAuthorizationCodeType(BenerailBaseModel):
    identifier: float | None = Field(None, alias="id")
    name: str | None = None
    href: str | None = None


class RcodeAuthorizationCode(BenerailBaseModel):
    identifier: float | None = Field(None, alias="id")
    href: str | None = None


class RcodeAuthorization(BenerailBaseModel):
    last_update_at: date | None = Field(None, example="2020-10-25")
    authorization_group: RcodeAuthorizationAuthorizationGroup | None = None
    code_type: RcodeAuthorizationCodeType | None = None
    code: RcodeAuthorizationCode | None = None
