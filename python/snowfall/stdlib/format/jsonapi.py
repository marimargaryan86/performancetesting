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
    TypeVar,
    final,
    get_args,
    get_origin,
)

import pydantic
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


class ResourceModel(pydantic.BaseModel):
    _type: ClassVar[str]
    id: str
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

    @pydantic.model_serializer(mode="wrap", when_used="always", return_type=Resource)
    def _serialize(self, serializer: Callable[[Self], Mapping[str, Any]]) -> Resource:
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
class RelationshipModel(pydantic.BaseModel, Generic[_Relationship]):
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
