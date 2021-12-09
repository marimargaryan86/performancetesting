from typing import Any, Mapping, Optional, Sequence, Union

import pydantic
from starlette import responses

AnyMapping = Mapping[str, Any]


class ResourceIdentifier(pydantic.BaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    data_type: str = pydantic.Field(..., alias="type")


class Resource(ResourceIdentifier):
    attributes: Optional[AnyMapping] = None
    relationships: Optional[AnyMapping] = None
    links: Optional[AnyMapping] = None
    meta: Optional[AnyMapping] = None


ResourceType = Union[ResourceIdentifier, Sequence[ResourceIdentifier]]


class Error(pydantic.BaseModel):
    status: str
    title: str
    detail: str


class Body(pydantic.BaseModel):
    resource_data: Optional[ResourceType] = pydantic.Field(None, alias="data")
    errors: Optional[Sequence[Error]] = None
    meta: Optional[AnyMapping] = None
    links: Optional[AnyMapping] = None


class JsonApiResponse(responses.JSONResponse):
    media_type = "application/vnd.api+json"

    def __init__(
        self,
        body: Body,
        status_code: int = 200,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            content=body.dict(exclude_unset=True, by_alias=True),
            status_code=status_code,
            headers=headers or {},
        )
