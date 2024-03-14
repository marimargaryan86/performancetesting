import abc
from collections.abc import Callable, Mapping
from typing import Any, NotRequired, Self

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


class Model(pydantic.BaseModel, abc.ABC):
    id: str
    model_config = pydantic.ConfigDict(extra="forbid", strict=True)

    @property
    @abc.abstractmethod
    def type(self) -> str:
        raise NotImplementedError

    @pydantic.model_serializer(mode="wrap", when_used="always", return_type=Resource)
    def _serialize(self, serializer: Callable[[Self], Mapping[str, Any]]) -> Resource:
        as_dict = serializer(self)

        return {
            "id": as_dict["id"],
            "type": self.type,
            "attributes": {key: value for key, value in as_dict.items() if key != "id"},
        }

    @pydantic.model_validator(mode="before")
    @classmethod
    def _validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        try:
            is_dict = isinstance(data["attributes"], dict)
        except KeyError:
            is_dict = False

        return {
            **(data["attributes"] if is_dict else {}),
            **{
                key: value
                for key, value in data.items()
                if key not in {"attributes", "type"}
            },
        }
