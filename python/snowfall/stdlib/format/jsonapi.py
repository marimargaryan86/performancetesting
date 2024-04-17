import functools
import inspect
import types
from collections.abc import Callable, Mapping
from typing import (
    Any,
    ClassVar,
    Generic,
    NotRequired,
    Self,
    TypeAlias,
    TypeVar,
    final,
    get_args,
    get_origin,
)

import pydantic
from pydantic.alias_generators import to_camel as pydantic_to_camel
from typing_extensions import TypedDict


class Links(TypedDict):
    next: NotRequired[str]
    related: NotRequired[str]
    self: NotRequired[str]  # noqa: WPS117


class ResourceIdentifier(TypedDict):
    id: NotRequired[str]
    type: str


class Relationship(TypedDict):
    links: NotRequired[Links]
    data: list[ResourceIdentifier] | ResourceIdentifier | None


class Resource(ResourceIdentifier):
    attributes: NotRequired[Mapping[str, object]]
    links: NotRequired[Links]
    relationships: NotRequired[Mapping[str, Relationship]]


def _flatten_relationships(
    relationships: Mapping[str, Relationship],
) -> dict[str, list[str] | str | None]:
    flattened: dict[str, list[str] | str | None] = {}

    for key, relationship in relationships.items():
        if relationship["data"] is None:
            flattened[key] = None
        elif isinstance(relationship["data"], dict):
            flattened[key] = relationship["data"]["id"]
        else:
            flattened[key] = [
                relationship_data["id"] for relationship_data in relationship["data"]
            ]

    return flattened


def flatten_resource(
    resource_data: Resource,
) -> dict[str, object | list[str] | str | None]:
    return {
        **resource_data.get("attributes", {}),
        **_flatten_relationships(resource_data.get("relationships", {})),
    }


class _BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic_to_camel,
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        strict=True,
    )


class MetaModel(_BaseModel):
    """Placeholder model to allow future extensions of functionality."""


class LinkModel(_BaseModel):
    href: pydantic.HttpUrl
    rel: str | None = None
    described_by: "_Link" = pydantic.Field(default=None, alias="describedby")
    title: str | None = None
    type: str | None = None
    href_lang: str | list[str] | None = pydantic.Field(default=None, alias="hreflang")
    meta: MetaModel | None = None


_Link: TypeAlias = pydantic.HttpUrl | LinkModel | None  # noqa: WPS465


class ResourceLinksModel(_BaseModel):
    self: _Link  # noqa: WPS117


class ResourceModel(_BaseModel):
    _type: ClassVar[str]
    id: str
    links: ResourceLinksModel | None = None
    meta: MetaModel | None = None
    model_config = pydantic.ConfigDict(extra="forbid", strict=True)

    @classmethod
    def type(cls) -> str:
        try:
            return cls._type
        except AttributeError:
            raise AttributeError(
                "{0} has no JSON:API type defined as a ClassVar.".format(
                    cls.__name__,
                ),
            ) from None

    @pydantic.model_serializer(mode="wrap", when_used="always")
    def _serialize(self, serializer: Callable[[Self], Mapping[str, Any]]) -> Any:
        as_dict = serializer(self)
        relationships = _relationship_fields(type(self))
        return_data: Resource = {
            "type": self.type(),
            "id": as_dict["id"],
            "attributes": {
                key: value
                for key, value in as_dict.items()
                if key != "id" and key not in relationships
            },
        }

        if relationships:
            return_data["relationships"] = {
                key: {"data": value}
                for key, value in as_dict.items()
                if key in relationships
            }

        return return_data

    @pydantic.model_validator(mode="before")
    @classmethod
    def _validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        attributes_is_dict = isinstance(data.get("attributes"), dict)
        relationships_is_dict = isinstance(data.get("relationships"), dict)

        if data.get("type") not in {cls.type(), None}:
            raise ValueError(
                "JSON:API type {0} does not match {1}".format(
                    data.get("type"),
                    cls.type(),
                ),
            )

        return {
            **(data["attributes"] if attributes_is_dict else {}),
            **(
                _validate_relationships(data["relationships"])
                if relationships_is_dict
                else {}
            ),
            **{
                key: value
                for key, value in data.items()
                if key not in {"attributes", "relationships", "type"}
            },
        }


def _validate_relationships(
    relationships: Mapping[str, Any],
) -> Mapping[str, list[ResourceIdentifier] | ResourceIdentifier | None]:
    return {
        relationship: resources["data"]
        if isinstance(resources, dict) and "data" in resources
        else resources
        for relationship, resources in relationships.items()
    }


_Relationship = TypeVar("_Relationship", bound=ResourceModel)


@final
class RelationshipModel(_BaseModel, Generic[_Relationship]):
    id: str
    model_config = pydantic.ConfigDict(extra="forbid", strict=True)

    @classmethod
    def type(cls) -> str:
        try:
            resource = cls.__pydantic_generic_metadata__["args"][0]
        except (IndexError, KeyError):
            raise TypeError(
                "Missing type parameters for generic type {0}.".format(
                    cls.__name__,
                ),
            ) from None

        try:
            return resource.type()
        except AttributeError:
            raise AttributeError(
                "{0} has no JSON:API type defined as a ClassVar.".format(
                    resource.__name__,
                ),
            ) from None

    @pydantic.model_serializer(
        mode="wrap",
        when_used="always",
        return_type=ResourceIdentifier,
    )
    def _serialize(
        self,
        serializer: Callable[[Self], Mapping[str, Any]],
    ) -> ResourceIdentifier:
        as_dict = serializer(self)

        return {
            "type": self.type(),
            "id": as_dict["id"],
        }

    @pydantic.model_validator(mode="before")
    @classmethod
    def _validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get("type") not in {cls.type(), None}:
            raise ValueError(
                "JSON:API type {0} does not match {1}".format(
                    data.get("type"),
                    cls.type(),
                ),
            )

        try:
            return {"id": data["id"]}
        except KeyError:
            return data


@functools.cache
def _relationship_fields(model: type[ResourceModel]) -> set[str]:
    return {
        field
        for field, info in model.model_fields.items()
        if _is_relationship(info.annotation)
    }


def _is_relationship(annotation: type[Any] | None) -> bool:
    if inspect.isclass(annotation) and issubclass(annotation, RelationshipModel):
        return True

    if get_origin(annotation) not in {list, types.UnionType}:
        return False

    return all(
        issubclass(arg, RelationshipModel) or arg is types.NoneType
        for arg in get_args(annotation)
    )


class ErrorLinksModel(_BaseModel):
    about: _Link = None
    type: _Link = None


class ErrorModel(_BaseModel):
    id: str | None = None
    links: ErrorLinksModel | None = None
    status: str | None = None
    code: str | None = None
    title: str | None = None
    detail: str | None = None
    # TODO(jyggen): source
    meta: MetaModel | None = None

    @pydantic.model_validator(mode="after")
    def _validate(self) -> Any:
        is_any_set = any([
            self.id,
            self.status,
            self.code,
            self.title,
            self.detail,
        ])

        if not is_any_set:
            raise ValueError("An error object MUST contain at least one member.")


class DocumentLinksModel(_BaseModel):
    self: _Link = None  # noqa: WPS117
    related: _Link = None
    described_by: _Link = pydantic.Field(default=None, alias="describedby")
    first: _Link = None
    last: _Link = None
    prev: _Link = None
    next: _Link = None


class JsonApiModel(_BaseModel):
    version: str | None = None
    ext: list[pydantic.HttpUrl] | None = None
    profile: list[pydantic.HttpUrl] | None = None
    meta: MetaModel | None = None


_ResourceType = TypeVar("_ResourceType", bound=ResourceModel)
_IncludeType = TypeVar("_IncludeType", bound=ResourceModel)


class DocumentModel(_BaseModel, Generic[_ResourceType, _IncludeType]):
    data: ResourceModel | list[_ResourceType] | None = None
    errors: list[ErrorModel] | None = None
    meta: MetaModel | None = None
    jsonapi: JsonApiModel | None = None
    links: DocumentLinksModel | None = None
    included: list[_IncludeType] | None = None
