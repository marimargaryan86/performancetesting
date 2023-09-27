import datetime
from typing import Any

import pydantic


class OAuth2Client(pydantic.BaseModel):
    client_id: str
    owner: str


class Traits(pydantic.BaseModel):
    email: str


class Identity(pydantic.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    traits: Traits
    metadata_public: dict[str, Any] = pydantic.Field(default_factory=dict)

    @pydantic.model_validator(mode="before")
    @classmethod
    def _remove_none(cls, payload: Any) -> Any:
        if isinstance(payload, dict):
            payload = {
                data_key: data_value
                for data_key, data_value in payload.items()
                if data_value is not None
            }

        return payload


class Session(pydantic.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    active: bool
    expires_at: datetime.datetime
    identity: Identity
