from typing import Optional

from pydantic import EmailStr
from pydantic.fields import Field

from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema


class AccountLoginSchema(BaseSchema):
    email: EmailStr
    password: str


class AccountForgotPasswordSchema(BaseSchema):
    email: EmailStr


class AccountResponseSchema(BaseSchema):
    id_: int = Field(alias="id")
    email: str
    firstname: str
    lastname: str


class AccountDetailedResponseSchema(AccountResponseSchema):
    mobile: str
    active: bool
    token: str
    created: Optional[int]
    modified: Optional[int]


class AdminAccountDetailedResponseSchema(AccountDetailedResponseSchema):
    admin: bool
    staff: bool
    support: bool
    flirtboard: bool
    stadler: bool
    operator: bool
