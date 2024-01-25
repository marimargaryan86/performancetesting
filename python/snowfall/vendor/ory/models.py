import datetime
from typing import Any

import pydantic

from snowfall.stdlib.integration.pydantic import model
from snowfall.stdlib.v1.cursor_pb2 import Cursor


class OAuth2Client(pydantic.BaseModel):
    client_id: str
    owner: str


class Traits(pydantic.BaseModel):
    email: str


class Identity(model.DefaultingBaseModel):
    identifier: str = pydantic.Field(alias="id")
    traits: Traits
    metadata_public: dict[str, Any] = pydantic.Field(default_factory=dict)


class IdentitiesPage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    identities: list[Identity]
    next_page_token: Cursor | None = None


class Session(pydantic.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    active: bool
    expires_at: datetime.datetime
    identity: Identity
