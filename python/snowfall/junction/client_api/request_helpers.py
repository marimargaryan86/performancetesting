from typing import Any

from starlette import requests

_IDENTIFIER = "id"


async def flatten_request(request: requests.Request) -> dict[str, Any]:
    return await flatten_request_body(await request.json())


async def flatten_request_body(body: dict[str, Any]) -> dict[str, Any]:
    return await _flatten_data(body["data"])


async def _flatten_relationships(relationships: dict[str, Any]) -> dict[str, Any]:
    flattened = {}

    for key, relationship in relationships.items():
        flattened[key] = relationship["data"][_IDENTIFIER]

    return flattened


async def _flatten_data(resource_data: dict[str, Any]) -> dict[str, Any]:
    flattened = {}

    if resource_data.get("attributes"):
        flattened.update(resource_data["attributes"])

    if resource_data.get("relationships"):
        flattened.update(await _flatten_relationships(resource_data["relationships"]))

    return flattened
