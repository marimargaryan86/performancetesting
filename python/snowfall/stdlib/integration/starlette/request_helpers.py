from collections.abc import Mapping
from typing import Any

from starlette import requests

from snowfall.stdlib.format import jsonapi


async def flatten_request(request: requests.Request) -> dict[str, Any]:
    return flatten_request_body(await request.json())


def flatten_request_body(body: Mapping[str, Any]) -> dict[str, Any]:
    return jsonapi.flatten_resource(body["data"])
