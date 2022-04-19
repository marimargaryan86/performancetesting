import dataclasses
from typing import Any, Mapping, Optional, Sequence

from starlette import requests

_IDENTIFIER = "id"
_DATA_KEY = "data"


async def flatten_request(request: requests.Request) -> dict[str, Any]:
    return flatten_request_body(await request.json())


def flatten_request_body(body: Mapping[str, Any]) -> dict[str, Any]:
    return _flatten_data(body[_DATA_KEY])


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


def _flatten_data(resource_data: Mapping[str, Any]) -> dict[str, Any]:
    flattened = {}

    if resource_data.get("attributes"):
        flattened.update(resource_data["attributes"])

    if resource_data.get("relationships"):
        flattened.update(_flatten_relationships(resource_data["relationships"]))

    return flattened


@dataclasses.dataclass(frozen=True)
class SequencePage(object):
    sequence: Sequence[Any]
    next_page_token: Optional[int] = None


async def sequence_paginator(
    sequence: Sequence[Any],
    limit: int,
    cursor: int = 0,
) -> SequencePage:
    start_index = cursor
    end_index = cursor + limit

    return SequencePage(
        sequence=sequence[start_index:end_index],
        next_page_token=end_index,  # TODO: what if index exceeds length?
    )
