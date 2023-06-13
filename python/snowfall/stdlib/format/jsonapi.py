from collections.abc import Mapping
from typing import Any

_DATA_KEY = "data"
_IDENTIFIER = "id"


def _flatten_relationships(relationships: Mapping[str, Any]) -> dict[str, Any]:
    flattened = {}

    for key, relationship in relationships.items():
        if isinstance(relationship[_DATA_KEY], dict):
            flattened[key] = relationship[_DATA_KEY][_IDENTIFIER]
        else:
            flattened[key] = []
            for relationship_data in relationship[_DATA_KEY]:
                flattened[key].append(relationship_data[_IDENTIFIER])

    return flattened


def flatten_resource(resource_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **resource_data.get("attributes", {}),
        **_flatten_relationships(resource_data.get("relationships", {})),
    }
