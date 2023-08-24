import datetime

from pydantic import v1 as pydantic


class OAuth2Client(pydantic.BaseModel):
    client_id: str
    owner: str


class Traits(pydantic.BaseModel):
    email: str


class Identity(pydantic.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    traits: Traits


class Session(pydantic.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    active: bool
    expires_at: datetime.datetime
    identity: Identity
