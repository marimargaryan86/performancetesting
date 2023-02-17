from typing import Optional

from pydantic import EmailStr
from pydantic.fields import Field

from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema


class AccountLoginSchema(BaseSchema):
    email: EmailStr
    password: str


class AccountResponseSchema(BaseSchema):
    id_: int = Field(alias="id")
    email: str
    firstname: str
    lastname: str


class AccountDetailedResponseSchema(AccountResponseSchema):
    mobile: str
    active: bool
    created: Optional[int]
    modified: Optional[int]
