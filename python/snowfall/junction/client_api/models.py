from typing import Any, Optional, Union

import pydantic
from starlette import responses

AnyDict = dict[str, Any]


class ResourceIdentifier(pydantic.BaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    data_type: str = pydantic.Field(..., alias="type")


class Resource(ResourceIdentifier):
    attributes: Optional[AnyDict] = None
    relationships: Optional[AnyDict] = None
    links: Optional[AnyDict] = None
    meta: Optional[AnyDict] = None


ResourceType = Optional[Union[ResourceIdentifier, list[ResourceIdentifier]]]


class Error(pydantic.BaseModel):
    status: str
    title: str
    detail: str


class Body(pydantic.BaseModel):
    resource_data: ResourceType = pydantic.Field(None, alias="data")
    errors: Optional[list[Error]] = None
    meta: Optional[AnyDict] = None
    links: Optional[AnyDict] = None


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
