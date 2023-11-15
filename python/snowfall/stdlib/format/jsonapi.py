from collections.abc import Mapping
from typing import NotRequired, TypedDict


class ResourceIdentifier(TypedDict):
    id: NotRequired[str]
    type: str


class Relationship(TypedDict):
    data: list[ResourceIdentifier] | ResourceIdentifier | None


class Resource(ResourceIdentifier):
    attributes: NotRequired[dict[str, object]]
    relationships: NotRequired[dict[str, Relationship]]


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
