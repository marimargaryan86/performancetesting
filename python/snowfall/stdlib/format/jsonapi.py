from collections.abc import Mapping
from typing import Any


def _flatten_relationships(relationships: Mapping[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}

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


def flatten_resource(resource_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **resource_data.get("attributes", {}),
        **_flatten_relationships(resource_data.get("relationships", {})),
    }
