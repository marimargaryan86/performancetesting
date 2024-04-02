import asyncio
import json
import time
from collections.abc import Callable, Mapping
from itertools import starmap
from typing import Any


def generate_curl_command(
    base_url: str,
    method: str,
    url: str,
    cookie_header: Mapping[str, Any] | None = None,
    token: str | None = None,
    query_parameters: Mapping[str, str] | None = None,
    body: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> str:
    full_url = str(base_url) + url
    curl_command = 'curl -X "{0}" "{1}"'.format(method, full_url)

    if query_parameters:
        curl_command += ' -d "{0}"'.format(
            json.dumps(query_parameters).replace('"', r"\""),
        )
    header_strings = []
    if headers:
        header_strings.extend(
            list(starmap(' -H "{0}: {1}"'.format, headers.items())),
        )
    if cookie_header:
        header_strings.append(' -H "Cookie: {0}"'.format(cookie_header))

    curl_command += " ".join(header_strings)

    if token:
        curl_command += ' -H "Authorization: Bearer {0}"'.format(token)
    if body:
        curl_command += ' -H "Content-Type: application/vnd.api+json" -d "{0}"'.format(
            json.dumps(body).replace('"', r"\""),
        )

    return "Curl command for the {0} request:\n{1}".format(method, curl_command)


def get_nested_attribute(data: Mapping[Any, Any], path: str) -> Any:  # noqa: WPS229
    try:  # noqa: WPS229
        keys = path.split(".")
        for key in keys:
            index_or_key = int(key) if key.isdigit() else key
            data = data[index_or_key]
    except (KeyError, TypeError, IndexError):
        return None
    else:
        return data


async def poll_until_condition_met(
    request_func: Callable[[], Any],
    attribute_path: str,
    success_value: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 5,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while time.time() < stopwatch:
        response = await request_func()
        if get_nested_attribute(data=response, path=attribute_path) == success_value:
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)
